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

from tqdm import tqdm

from climetlab.core.settings import SETTINGS
from climetlab.decorators import alias_argument
from climetlab.readers.grib.fieldset import FieldSet
from climetlab.scripts.grib import _index_grib_file

LOG = logging.getLogger(__name__)


class IndexedSource(FieldSet):

    _reader_ = None

    @alias_argument("levelist", ["level"])
    @alias_argument("param", ["variable", "parameter"])
    @alias_argument("number", ["realization", "realisation"])
    @alias_argument("class", "klass")
    def __init__(self, path=None, dic=None, filter=None, merger=None, **kwargs):
        print(kwargs)
        self.path = path
        self.abspath = os.path.abspath(path)
        self._climetlab_index_file = os.path.join(self.abspath, "climetlab.index")
        self._index = None
        self.filter = filter
        self.merger = merger

        if dic:
            assert isinstance(
                dic, dict
            ), f"Expected a dict, but argument was dic={dic}."
            for k, v in dic.items():
                assert k not in kwargs, f"Duplicated key {k}={v} and {k}={kwargs[k]}"
                kwargs[k] = v

        self.kwargs_selection = kwargs

        fields = self.kwargs_to_fields(kwargs)
        LOG.debug("Got iterator")
        fields = list(fields)
        LOG.debug("Transformed into a list of ({len(fields)} elements.")
        super().__init__(fields=fields)

    def kwargs_to_fields(self, kwargs):
        for path, parts in tqdm(self.index.lookup_request(kwargs)):
            assert path[:5] == "file:", path
            path = path[5:]
            for offset, length in parts:
                yield (path, offset, length)

    def sel(self, **kwargs):
        new_kwargs = {k: v for k, v in self.kwargs_selection.items()}
        new_kwargs.update(kwargs)
        return IndexedSource(
            self.path, filter=self.filter, merger=self.merger, **new_kwargs
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

    def _create_index(self):
        assert os.path.isdir(self.path)
        for root, _, files in os.walk(self.path):
            for name in files:
                if name == "climetlab.index":
                    continue
                p = os.path.abspath(os.path.join(root, name))
                yield from _index_grib_file(p, path_name=name)

    @property
    def index(self):
        if self._index is not None:
            return self._index

        from climetlab.indexing import DirectoryGlobalIndex

        if os.path.exists(self._climetlab_index_file):
            self._index = DirectoryGlobalIndex(
                self._climetlab_index_file, path="file://" + self.abspath
            )
            return self._index

        print("Creating index for", self.path, " into ", self._climetlab_index_file)
        entries = self._create_index()
        # TODO: create .tmp file and move it (use cache_file)
        with open(self._climetlab_index_file, "w") as f:
            for e in entries:
                json.dump(e, f)
                print("", file=f)

        print("Created index file", self._climetlab_index_file)
        return self.index


source = IndexedSource
