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
class LocalSource(FieldSet):

    _reader_ = None

    def __init__(self, path=None, filter=None, merger=None, **kwargs):
        self.path = path
        self._index_file = os.path.join(path, "climetlab.index")
        self._index = None
        self.filter = filter
        self.merger = merger

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
        path = getattr(self, "path", None)
        if isinstance(path, str):
            path = path.replace(cache_dir, "CACHE:")
        return f"{self.__class__.__name__}({path})"

    def _create_index(self):
        print("Creating index for", self.path)
        assert os.path.isdir(self.path)
        for root, _, files in os.walk(self.path):
            for name in files:
                if name == "climetlab.index":
                    continue
                p = os.path.join(root, name)
                # p = os.path.relpath(name, start = self.path)
                yield from _index_grib_file(p)

    @property
    def index(self):
        if self._index is not None:
            return self._index

        from climetlab.indexing import GlobalIndex

        if os.path.exists(self._index_file):
            # TODO: adapt GlobalIndex to process files.
            self._index = GlobalIndex(self._index_file, baseurl="file:")
            print("Read index file", self._index_file)
            return self._index

        entries = self._create_index()
        # TODO: create .tmp file and move it (use cache_file)
        with open(self._index_file, "w") as f:
            for e in entries:
                print(json.dump(e, f))
                print("", file=f)

        print("Created index file", self._index_file)
        return self.index


source = LocalSource
