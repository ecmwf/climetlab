# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import logging
import os
import warnings
from abc import abstractmethod
from collections import namedtuple
from urllib.parse import urljoin

import requests
from multiurl import robust

from climetlab.core.caching import auxiliary_cache_file, cache_file
from climetlab.core.index import Index, MultiIndex, Order
from climetlab.decorators import cached_method
from climetlab.indexing.database.json import JsonDatabase
from climetlab.indexing.database.sql import SqlDatabase
from climetlab.readers.grib.codes import GribField, get_messages_positions
from climetlab.readers.grib.fieldset import FieldSet
from climetlab.utils import progress_bar
from climetlab.utils.kwargs import merge_for_selection
from climetlab.utils.parts import Part
from climetlab.utils.serialise import register_serialisation
from climetlab.vocabularies.grib import grib_naming

LOG = logging.getLogger(__name__)


class GribOrder(Order):
    def __init__(self, *args, **kwargs):
        kwargs = grib_naming(kwargs)
        if len(args) == 1 and isinstance(args[0], dict):
            args = [grib_naming(args[0])]

        super().__init__(*args, **kwargs)


class GribIndex(FieldSet, Index):
    ORDER_CLASS = GribOrder

    def __init__(self, **kwargs):

        self._availability = None
        super().__init__(**kwargs)


class MultiGribIndex(FieldSet, MultiIndex):
    def __init__(self, *args, **kwargs):
        MultiIndex.__init__(self, *args, **kwargs)


class GribInFiles(GribIndex):
    def __getitem__(self, n):
        part = self.part(n)
        return GribField(part.path, part.offset, part.length)

    def __len__(self):
        return self.number_of_parts()

    @abstractmethod
    def part(self, n):
        self._not_implemented()

    @abstractmethod
    def number_of_parts(self):
        self._not_implemented()


class GribDBIndex(GribInFiles):
    def __init__(self, db, **kwargs):
        """Should not be instanciated directly.
        The public API are the constructors "_from*()" class methods.
        """

        self.db = db
        self.selection = {}
        self.order = {}

        # self._cache is a tuple : (first, length, result). It holds one chunk of the db.
        # The third element (result) is a list of size length.
        self._cache = None

        super().__init__(**kwargs)

    def no_sel(self, *args, **kwargs):
        if not kwargs:  # no kwargs
            if not args or (len(args) == 1 and not args[0]):  # and no args
                return self

        selection = merge_for_selection(self.selection, args, kwargs)
        return self.__class__(
            db=self.db,
            selection=selection,
            order=self.order,
        )

    def no_order_by(self, *args, **kwargs):

        order = self.ORDER_CLASS(*args, **kwargs)
        if order.is_empty:
            return self

        return self.__class__(
            db=self.db,
            selection=self.selection,
            order=order,
        )

    @classmethod
    def from_iterator(
        cls,
        iterator,
        cache_metadata,
        selection=None,
        order_by=None,
        **kwargs,
    ):
        def load(target, *args):
            LOG.debug(f"Building db in {target}")
            db = cls.DBCLASS(target)
            db.load(iterator)

        db_name = cache_file(
            "grib-index",
            load,
            cache_metadata,
            hash_extra=cls.DBCLASS.VERSION,
            extension=cls.DBCLASS.EXTENSION,
        )

        db = cls.DBCLASS(db_name)

        new = cls(db=db, **kwargs)
        new = new.sel(selection)
        new = new.order_by(order_by)
        return new

    @classmethod
    def from_url(cls, url, patch_entry=None, **kwargs):
        """Create a database from a given url"""

        # If this is a file, open it without download
        if os.path.exists(url):
            return cls.from_file(path=url, **kwargs)
        if url.startswith("file://") and os.path.exists(url[7:]):
            return cls.from_file(path=url[7:], **kwargs)

        # Request to download the data
        r = robust(requests.get)(url, stream=True)
        r.raise_for_status()
        try:
            size = int(r.headers.get("Content-Length"))
        except Exception:
            size = None

        if patch_entry is None:

            def absolute_url(entry):  # closure on "url"
                entry["_path"] = urljoin(url, entry.pop("_path"))
                return entry

            patch_entry = absolute_url

        def progress(iterable):
            pbar = progress_bar(iterable=iterable, desc="Downloading index", total=size)
            for line in pbar:
                yield line
                pbar.update(len(line) + 1)

        def parse_lines(lines):
            for line in lines:
                entry = json.loads(line)
                entry = patch_entry(entry)
                yield entry

        iterator = r.iter_lines()
        iterator = progress(iterator)
        iterator = parse_lines(iterator)

        return cls.from_iterator(
            iterator=iterator,
            cache_metadata={"url": url},
            **kwargs,
        )

    @classmethod
    def from_file(cls, path, **kwargs):
        directory = os.path.dirname(path)
        size = os.path.getsize(path)

        def progress(lines):
            pbar = progress_bar(iterable=lines, desc="Parsing index", total=size)
            for line in pbar:
                yield line
                pbar.update(len(line) + 1)

        def parse_lines(lines):
            for line in lines:
                entry = json.loads(line)
                if not os.path.isabs(entry["_path"]):
                    entry["_path"] = os.path.join(directory, entry["_path"])
                yield entry

        iterator = open(path)
        iterator = progress(iterator)
        iterator = parse_lines(iterator)

        return cls.from_iterator(
            iterator=iterator,
            cache_metadata={"path": path},
            **kwargs,
        )

    @classmethod
    def from_existing_db(cls, db_path, **kwargs):
        assert os.path.exists(db_path)
        return cls(cls.DBCLASS(db_path), **kwargs)

    @property
    def availability(self):
        if self._availability is not None:
            return self._availability.tree()

        print(
            (
                "FIXME: TODO: bug here: should not call dump_dicts"
                " (dumping all dicts) but should call lookup(self.selection..) "
            )
        )

        def f():
            for i in self.db.dump_dicts():
                i = {k: v for k, v in i.items() if not k.startswith("_")}
                yield i

        from climetlab.utils.availability import Availability

        LOG.debug("Building availability")
        self._availability = Availability(f())
        return self.availability


class JsonIndex(GribDBIndex):
    DBCLASS = JsonDatabase

    def __init__(self):
        assert False

    @cached_method
    def _lookup_parts(self):
        return self.db.lookup_parts()

    def part(self, n):
        return self._lookup_parts()[n]

    def number_of_parts(self):
        return len(self._lookup_parts())


SqlIndexCache = namedtuple("SqlIndexCache", ["first", "length", "result"])


class SqlIndex(GribDBIndex):

    DBCLASS = SqlDatabase
    CHUNKING = 50000

    def sel(self, *args, **kwargs):
        selection = self.SELECTION_CLASS(*args, **kwargs)
        if selection.is_empty:
            return self
        db = self.db.sel(selection=selection)
        return self.__class__(db=db)

    def order_by(self, *args, **kwargs):
        order = self.ORDER_CLASS(*args, **kwargs)
        if order.is_empty:
            return self
        db = self.db.order_by(order=order)
        return self.__class__(db=db)

    def part(self, n):
        if self._cache is None or not (
            self._cache.first <= n < self._cache.first + self._cache.length
        ):
            first = n // self.CHUNKING
            result = self.db.lookup_parts(limit=self.CHUNKING, offset=first)
            self._cache = SqlIndexCache(first, len(result), result)
        return self._cache.result[n % self.CHUNKING]

    @cached_method
    def number_of_parts(self):
        return self.db.count()


register_serialisation(
    SqlIndex,
    lambda x: x.db.db_path,
    lambda x: SqlIndex(db=SqlDatabase(x)),  # TODO: add selection and order here?
)


class GribFileIndex(GribInFiles):
    VERSION = 1

    def __init__(self, path, **kwargs):
        assert isinstance(path, str), path

        self.path = path
        self.offsets = None
        self.lengths = None
        self.cache = auxiliary_cache_file(
            "grib-index",
            path,
            content="null",
            extension=".json",
        )

        if not self._load_cache():
            self._build_index()

        super().__init__(**kwargs)

    def _build_index(self):

        offsets = []
        lengths = []

        for offset, length in get_messages_positions(self.path):
            offsets.append(offset)
            lengths.append(length)

        self.offsets = offsets
        self.lengths = lengths

        self._save_cache()

    def _save_cache(self):
        try:
            with open(self.cache, "w") as f:
                json.dump(
                    dict(
                        version=self.VERSION,
                        offsets=self.offsets,
                        lengths=self.lengths,
                    ),
                    f,
                )
        except Exception:
            LOG.exception("Write to cache failed %s", self.cache)

    def _load_cache(self):
        try:
            with open(self.cache) as f:
                c = json.load(f)
                if not isinstance(c, dict):
                    return False

                assert c["version"] == self.VERSION
                self.offsets = c["offsets"]
                self.lengths = c["lengths"]
                return True
        except Exception:
            LOG.exception("Load from cache failed %s", self.cache)

        return False

    def part(self, n):
        return Part(self.path, self.offsets[n], self.lengths[n])

    def number_of_parts(self):
        return len(self.offsets)
