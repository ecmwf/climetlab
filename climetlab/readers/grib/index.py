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
from collections import namedtuple
from urllib.parse import urljoin

import requests
from multiurl import robust

from climetlab.core.caching import cache_file
from climetlab.core.index import Index
from climetlab.readers.grib.codes import CodesReader, GribField
from climetlab.utils import cached_method, tqdm
from climetlab.utils.availability import Availability

LOG = logging.getLogger(__name__)


class ItemWrapperForCfGrib:
    def __init__(self, item):
        self.item = item

    def __getitem__(self, n):
        print("asking for key:", n, self.item)
        if n == "values":
            return self.item.values
        return self.item.metadata(n)


class IndexWrapperForCfGrib:
    def __init__(self, index):
        self.index = index

    def __getitem__(self, n):
        print(n, len(self))
        return ItemWrapperForCfGrib(self.index[n])

    def __len__(self):
        return len(self.index)


class GribIndex(Index):
    def __init__(self, selection=None, order=None):
        """Should not be instanciated directly.
        The public API are the constructors "_from*()" class methods.
        """

        self._availability = None
        self.selection = selection
        self.order = order


class GribDBIndex(GribIndex):
    VERSION = 3
    EXTENSION = None  # should be overrided

    def __init__(self, db, cache_metadata, db_path=None, selection=None, order=None):
        """Should not be instanciated directly.
        The public API are the constructors "_from*()" class methods.
        """

        self.cache_metadata = cache_metadata

        self.db = db
        self.db_path = db_path
        # self.db.reset_connection(db_path=db_path)

        # self._cache is a tuple : (first, length, result). It holds one chunk of the db.
        # The third element (result) is a list of size length.
        self._cache = None

        super().__init__(selection=selection, order=order)

    @classmethod
    def from_iterator(
        cls, iterator, cache_metadata, selection=None, order=None, db_path=None
    ):
        db = None

        def load(target, *args):
            LOG.debug(f"Building db in {target}")
            nonlocal db  # to make sure to use the variable db outside of the function
            db = cls.database_class(iterator=iterator, db_path=target)

        if db_path is not None:
            load(db_path)
        else:
            db_path = cache_file(
                "grib-index",
                load,
                cache_metadata,
                hash_extra=cls.VERSION,
                extension=cls.EXTENSION,
            )
            db.reset_connection(db_path=db_path)

        return cls(
            db=db,
            db_path=db_path,
            cache_metadata=cache_metadata,
            selection=selection,
            order=order,
        )

    @classmethod
    def from_url(cls, url, db_path=None):
        if os.path.exists(url):
            return cls.from_file(path=url, db_path=db_path)

        if url.startswith("file://") and os.path.exists(url[7:]):
            return cls.from_file(path=url[7:], db_path=db_path)

        r = robust(requests.get)(url, stream=True)
        r.raise_for_status()
        try:
            size = int(r.headers.get("Content-Length"))
        except Exception:
            size = None

        def progress(lines):
            pbar = tqdm(
                iterable=lines,
                desc="Downloading index",
                total=size,
                unit_scale=True,
                unit="B",
                leave=False,
                disable=False,
                unit_divisor=1024,
            )
            for line in pbar:
                yield line
                pbar.update(len(line) + 1)

        def parse_lines(lines):
            for line in lines:
                entry = json.loads(line)
                entry["_path"] = urljoin(url, entry["_path"])
                yield entry

        iterator = r.iter_lines()
        iterator = progress(iterator)
        iterator = parse_lines(iterator)

        return cls.from_iterator(
            iterator=iterator, db_path=db_path, cache_metadata={"url": url}
        )

    @classmethod
    def from_file(cls, path, db_path=None):
        directory = os.path.dirname(path)

        def parse_lines(lines):
            for line in lines:
                entry = json.loads(line)
                if not os.path.isabs(entry["_path"]):
                    entry["_path"] = os.path.join(directory, entry["_path"])
                yield entry

        iterator = parse_lines(open(path).readlines())

        return cls.from_iterator(
            iterator=iterator,
            db_path=db_path,
            cache_metadata={"path": path},
        )

    @classmethod
    def from_scanner(cls, scanner, db_path=None, cache_metadata=None):
        if cache_metadata is None:
            cache_metadata = {}
        return cls.from_iterator(
            iterator=scanner, db_path=db_path, cache_metadata=cache_metadata
        )

    def sort_index(self, order):
        return self.__class__(
            self.url, selection=self.selection, order=order, db=self.db
        )

    def sel(self, *args, **kwargs):
        sel = {}

        if self.selection:
            sel.update(self.selection)

        for a in args:
            sel.update(a)

        sel.update(kwargs)

        return self.__class__(
            selection=sel,
            order=self.order,
            db=self.db,
            cache_metadata=self.cache_metadata,
        )

    @property
    def availability(self, request=None):
        if request is None and self._availability is not None:
            return self._availability

        entries = self.lookup({}, select_values=True)
        availability = Availability(entries)

        if request is None:
            self._availability = availability

        return availability

    def to_xarray(self, **kwargs):
        # return self.fieldset.to_xarray(**kwargs)

        wrapped = IndexWrapperForCfGrib(self)
        import xarray as xr

        return xr.open_dataset(wrapped, engine="cfgrib")

    def __getitem__(self, n):
        self._not_implemented()


class GribIndexFromDicts(GribDBIndex):
    def __init__(self, list_of_dicts):
        self.list_of_dicts = list_of_dicts

    def __getitem__(self, n):
        class Wrapped(dict):
            def metadata(self, n):
                return self[n]

            @property
            def values(self, n):
                return self["values"]

        return Wrapped(self.list_of_dicts[n])

    def __len__(self):
        return len(self.list_of_dicts)


class GribIndexFromFile(GribDBIndex):
    _readers = None

    def _reader(self, path):
        if self._readers is None:
            self._readers = {}

        if path not in self._readers:
            self._readers[path] = CodesReader(path)
        return self._readers[path]

    def __getitem__(self, n):
        path, offset, length = self.part(n)
        reader = self._reader(path)
        field = GribField(reader, offset, length)
        return field

    def __len__(self):
        return self.number_of_parts()

    def part(self, n):
        self._not_implemented()

    def number_of_parts(self):
        self._not_implemented()


Cache = namedtuple("Cache", ["first", "length", "result"])


class JsonIndex(GribIndexFromFile):
    EXTENSION = ".json"

    @classmethod
    @property
    def database_class(self):
        from climetlab.indexing.database import JsonDatabase

        return JsonDatabase

    @cached_method
    def _lookup(self):
        return self.db.lookup(self.selection, order=self.order)

    def part(self, n):
        return self._lookup()[n]

    def number_of_parts(self):
        return len(self._lookup())


class SqlIndex(GribIndexFromFile):
    EXTENSION = ".db"
    CHUNK = 50000

    @classmethod
    @property
    def database_class(self):
        from climetlab.indexing.database import SqlDatabase

        return SqlDatabase

    def part(self, n):
        if self._cache is None or not (
            self._cache.first <= n < self._cache.first + self._cache.length
        ):
            first = n // self.CHUNK
            result = self.db.lookup(
                self.selection,
                order=self.order,
                limit=self.CHUNK,
                offset=first,
            )
            self._cache = Cache(first, len(result), result)
        return self._cache.result[n]

    @cached_method
    def number_of_parts(self):
        return self.db.count(self.selection)
