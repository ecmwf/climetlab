# (C) Copyright 2020 ECMWF.
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
from tqdm import tqdm

from climetlab.core import Base
from climetlab.core.caching import cache_file
from climetlab.core.settings import SETTINGS
from climetlab.decorators import alias_argument
from climetlab.sources import Source
from climetlab.utils.availability import Availability

LOG = logging.getLogger(__name__)


class Index(Base):
    def __getitem__(self, n):
        self._not_implemented()

    def __len__(self):
        self._not_implemented()

    def sel(self, kwargs):
        self._not_implemented()


class GribIndex(Index):
    VERSION = 3
    EXTENSION = ".DB"

    def __init__(
        self,
        cache_metadata,
        iterator=None,
        selection=None,
        order=None,
        db=None,
        db_path=None,
    ):

        self._availability = None
        self.selection = selection
        self.order = order
        self.cache_metadata = cache_metadata
        self.iterator = iterator

        # cache is a tuple : (first, length, result). It holds one chunk of the db.
        # The third element (result) is a list of size length.
        self._cache = None

        if db is not None:
            self.db = db
            self.db_path = db_path
            # self.db.reset_connection(db_path=db_path)
            return

        if db_path is not None:
            self.db = self.database_class(iterator=iterator, db_path=db_path)
            return

        def load(target, *args):
            print("Building db in ", target)
            self.db = self.database_class(iterator=iterator, db_path=target)

        db_path = cache_file(
            "index",
            load,
            cache_metadata,
            hash_extra=self.VERSION,
            extension=self.EXTENSION,
        )

        self.db.reset_connection(db_path=db_path)

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
                lines,
                desc="Downloading index",
                total=size,
                unit_scale=True,
                unit="B",
                leave=False,
                disable=False,
                unit_divisor=1024,
            )
            for line in pbar(lines):
                yield line
                pbar.update(len(line) + 1)

        def parse_lines(lines):
            for line in lines:
                entry = json.loads(line)
                entry["_path"] = urljoin(url, entry["_path"])
                yield entry

        iterator = r.iter_lines()
        iterator = progress(iterator)
        iterator = parse_lines(iterator, url)

        return cls(
            iterator=iterator,
            db_path=db_path,
            cache_metadata={"url": url},
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

        return cls(
            iterator=parse_lines(open(path).readlines()),
            db_path=db_path,
            cache_metadata={"path": path},
        )

    @classmethod
    def from_scanner(cls, scanner, db_path=None, cache_metadata=None):
        if cache_metadata is None:
            cache_metadata = {}
        return cls(iterator=scanner, db_path=db_path, cache_metadata=cache_metadata)

    def sort_index(self, order):
        return SqlIndex(self.url, selection=self.selection, order=order, db=self.db)

    def sel(self, selection):
        sel = {}
        if self.selection:
            sel.update(self.selection)
        if selection:
            sel.update(selection)
        return SqlIndex(
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

    def __len__(self):
        return len(self.lookup())

    #####################

    @property
    def fieldset(self):
        from climetlab.readers.grib.fieldset import FieldSet

        return FieldSet(self)

    def to_xarray(self, **kwargs):
        return self.fieldset.to_xarray(**kwargs)

    def number_of_parts(self):
        return len(self)

    def part(self, n):
        item = self[n]
        return item


class MaskIndex(Index):
    def __init__(self, index, indices):
        self.index = index
        self.indices = indices

    def __getitem__(self, n):
        n = self.indices[n]
        return self.index[n]

    def __len__(self):
        return len(self.indices)


class MultiIndex(Index):
    def __init__(self, indexes):
        self.indexes = list(indexes)

    def sel(self, *args, **kwargs):
        return MultiIndex(i.sel(*args, **kwargs) for i in self.indexes)

    def __getitem__(self, n):
        k = 0
        while n > len(self.indexes[k]):
            k += 1
            n -= len(self.indexes[k])
        return self.indexes[k][n]

    def __len__(self):
        return sum(len(i) for i in self.indexes)


Cache = namedtuple("Cache", ["first", "length", "result"])


class InMemoryIndex(GribIndex):
    EXTENSION = None

    @property
    def database_class(self):
        from climetlab.indexing.database import InMemoryDatabase

        return InMemoryDatabase

    def lookup(self, **kwargs):
        entries = self.db.lookup(self.selection, order=self.order, **kwargs)
        return [(x["_path"], x["_offset"], x["_length"]) for x in entries]

    def __getitem__(self, n):
        return self.lookup()[n]


class JsonIndex(GribIndex):
    EXTENSION = ".JSON"

    @property
    def database_class(self):
        from climetlab.indexing.database import JsonDatabase

        return JsonDatabase

    def lookup(self, **kwargs):
        entries = self.db.lookup(self.selection, order=self.order, **kwargs)
        return [(x["_path"], x["_offset"], x["_length"]) for x in entries]

    def __getitem__(self, n):
        return self.lookup()[n]


class SqlIndex(GribIndex):
    EXTENSION = ".SQL"
    CHUNK = 50000

    @property
    def database_class(self):
        from climetlab.indexing.database import SqlDatabase

        return SqlDatabase

    def lookup(self, **kwargs):
        return self.db.lookup(self.selection, order=self.order, **kwargs)

    def __getitem__(self, n):
        if self._cache is None or not (
            self._cache.first <= n < self._cache.first + self._cache.length
        ):
            first = n // self.CHUNK
            result = self.lookup(limit=self.CHUNK, offset=first)
            self._cache = Cache(first, len(result), result)
        return self._cache.result[n]


class IndexedSource(Source):

    _reader_ = None

    @alias_argument("levelist", ["level"])
    @alias_argument("param", ["variable", "parameter"])
    @alias_argument("number", ["realization", "realisation"])
    @alias_argument("class", "klass")
    def __init__(self, index=None, filter=None, merger=None, **kwargs):
        self.filter = filter
        self.merger = merger
        self.index = index.sel(kwargs)

        super().__init__()

    @property
    def availability(self):
        return self.index.availability

    def sel(self, **kwargs):
        return IndexedSource(
            self.path,
            filter=self.filter,
            merger=self.merger,
            index=self.index.sel(**kwargs),
        )

    def __getitem__(self, n):
        return self.index[n]

    def __len__(self):
        return len(self.index)

    def __repr__(self):
        cache_dir = SETTINGS.get("cache-directory")

        def to_str(attr):
            if not hasattr(self, attr):
                return None
            out = getattr(self, attr)
            if isinstance(out, str):
                out = out.replace(cache_dir, "CACHE:")
            return out

        args = [f"{x}={to_str(x)}" for x in ("path", "abspath")]
        args = [x for x in args if x is not None]
        args = ",".join(args)
        return f"{self.__class__.__name__}({args})"

    def to_tfdataset(self, *args, **kwargs):
        return self.index.to_tfdataset(*args, **kwargs)

    def to_pytorch(self, *args, **kwargs):
        return self.index.to_pytorch(*args, **kwargs)

    def to_numpy(self, *args, **kwargs):
        return self.index.to_numpy(*args, **kwargs)

    def to_xarray(self, *args, **kwargs):
        return self.index.to_xarray(*args, **kwargs)
