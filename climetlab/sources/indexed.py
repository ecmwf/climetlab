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

from climetlab.core import Base
from climetlab.core.settings import SETTINGS
from climetlab.decorators import alias_argument
from climetlab.scripts.grib import _index_grib_file
from climetlab.sources import Source

LOG = logging.getLogger(__name__)


class Index(Base):
    def __getitem__(self, n):
        self._not_implemented()

    def __len__(self):
        self._not_implemented()

    def sel(self, kwargs):
        self._not_implemented()


from climetlab.indexing.database import SqlDatabase


class SqlIndex(Index):
    def __init__(self, url):
        self.db = SqlDatabase(url=url)

    def lookup(self, request, **kwargs):
        return self.db.lookup(request, **kwargs)


class IndexedSource(Source):

    _reader_ = None

    @alias_argument("levelist", ["level"])
    @alias_argument("param", ["variable", "parameter"])
    @alias_argument("number", ["realization", "realisation"])
    @alias_argument("class", "klass")
    def __init__(self, index=None, filter=None, merger=None, **kwargs):
        self.filter = filter
        self.merger = merger
        self.index = index
        self.kwargs_selection = kwargs

        self._set_selection(kwargs)  # todo make it lazy

        super().__init__()

    def lookup_index(self):
        return self.index.get_path_offset_length(self.kwargs_selection)

    def sel(self, **kwargs):
        new_kwargs = {k: v for k, v in self.kwargs_selection.items()}
        new_kwargs.update(kwargs)
        return IndexedSource(
            self.path,
            filter=self.filter,
            merger=self.merger,
            index=self.index,
            **new_kwargs,
        )

    def __getitem__(self, n):
        return self.data_provider[n]

    def __len__(self):
        # todo ask index?
        return len(self.data_provider)

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
