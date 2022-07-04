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

from climetlab.core.settings import SETTINGS
from climetlab.readers.grib.fieldset import FieldSet
from climetlab.scripts.grib import _index_grib_file

LOG = logging.getLogger(__name__)


# TODO: rename 'local' to a more meaningful name
class IndexedSource(FieldSet):

    _reader_ = None

    def __init__(self, path=None, dic=None, filter=None, merger=None, **kwargs):
        self.path = path
        self.abspath = os.path.abspath(path)
        self._index_file = os.path.join(self.abspath, "climetlab.index")
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

        PARAMS_ALIASES = {
            "level": "levelist",
            "klass": "class",
            "parameter": "param",
            "variable": "param",
            "realization": "number",
        }
        for k, target in PARAMS_ALIASES.items():
            if k not in kwargs:
                continue
            assert target not in kwargs, (k, target)
            kwargs[target] = kwargs[k]
            del kwargs[k]

        # self.source = load_source("indexed-urls", self.index, kwargs)
        fields = []
        for path, parts in self.index.lookup_request(kwargs):
            assert path[:5] == "file:", path
            path = path[5:]  # hack to remove 'file:'
            for offset, length in parts:
                fields.append((path, offset, length))

        super().__init__(fields=fields)

    # def __len__(self):
    #     return len(self.source)

    # def to_xarray(self):
    #     return self.source.to_xarray()

    def __repr__(self):
        cache_dir = SETTINGS.get("cache-directory")
        path = self.path
        if isinstance(path, str):
            path = path.replace(cache_dir, "CACHE:")
        return f"{self.__class__.__name__}({path}, {self.abspath})"

    def _create_index(self):
        assert os.path.isdir(self.path)
        for root, _, files in os.walk(self.path):
            for name in files:
                if name == "climetlab.index":
                    continue
                # print('---')
                # print(name)
                p = os.path.abspath(os.path.join(root, name))
                # print(name)
                # name = os.path.relpath(name, start = self.abspath)
                # print(name)
                # print('*')
                yield from _index_grib_file(p, path_name=name)

    @property
    def index(self):
        if self._index is not None:
            return self._index

        from climetlab.indexing import GlobalIndex

        if os.path.exists(self._index_file):
            # TODO: adapt GlobalIndex to process files.
            self._index = GlobalIndex(
                self._index_file, baseurl="file://" + self.abspath
            )
            return self._index

        print("Creating index for", self.path, " into ", self._index_file)
        entries = self._create_index()
        # TODO: create .tmp file and move it (use cache_file)
        with open(self._index_file, "w") as f:
            for e in entries:
                json.dump(e, f)
                print("", file=f)

        print("Created index file", self._index_file)
        return self.index


source = IndexedSource
