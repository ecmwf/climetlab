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
from climetlab.readers.grib.fieldset import FieldSet
from climetlab.scripts.grib import _index_grib_file

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


class IndexedSource(FieldSet):

    _reader_ = None

    @alias_argument("levelist", ["level"])
    @alias_argument("param", ["variable", "parameter"])
    @alias_argument("number", ["realization", "realisation"])
    @alias_argument("class", "klass")
    def __init__(self, index=None, dic=None, filter=None, merger=None, **kwargs):
        self.filter = filter
        self.merger = merger
        self.index = index

        if dic:
            assert isinstance(
                dic, dict
            ), f"Expected a dict, but argument was dic={dic}."
            for k, v in dic.items():
                assert k not in kwargs, f"Duplicated key {k}={v} and {k}={kwargs[k]}"
                kwargs[k] = v

        self.kwargs_selection = kwargs

        def build_fields_iterator():
            for path, parts in self.index.lookup_request(kwargs):
                for offset, length in parts:
                    yield (path, offset, length)

        fields = build_fields_iterator()
        LOG.debug("Got iterator")
        fields = list(fields)
        LOG.debug("Transformed into a list of ({len(fields)} elements.")
        super().__init__(fields=fields)

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

    def __repr__(self):
        cache_dir = SETTINGS.get("cache-directory")

        def to_str(attr):
            if hasattr(self, attr):
                out = getattr(self, attr)
            else:
                out = "..."
            if isinstance(out, str):
                out = out.replace(cache_dir, "CACHE:")
            return out

        path = to_str("path")
        abspath = to_str("abspath")
        return f"{self.__class__.__name__}({path}, {abspath})"
