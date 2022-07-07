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

from climetlab.readers.grib.fieldset import FieldSet
from climetlab.scripts.grib import _index_grib_file
from climetlab.sources.indexed import IndexedSource, SqlIndex

LOG = logging.getLogger(__name__)


class DirectoryIndex(SqlIndex):
    def __init__(self, index_location, path) -> None:
        self.path = path
        self.abspath = os.path.abspath(path)
        self._climetlab_index_file = index_location

        if not os.path.exists(self._climetlab_index_file):
            print("Creating index for", self.path, " into ", self._climetlab_index_file)
            entries = self._parse_files(self.path)
            # TODO: create .tmp file and move it (use cache_file)
            with open(self._climetlab_index_file, "w") as f:
                for e in entries:
                    json.dump(e, f)
                    print("", file=f)
            print("Created index file", self._climetlab_index_file)

        super().__init__(self._climetlab_index_file)

    def get_path_offset_length(self, request):
        urls_parts = []
        for path, part in self.lookup(request, order=True):
            url = f"{self.path}/{path}"
            urls_parts.append((url, [part]))
        # TODO : here need to reorder according to user request?
        return urls_parts

    def _parse_files(self, path, ignore=("climetlab.index")):
        LOG.debug(f"Parsing files in {path}")
        assert os.path.isdir(path)
        for root, _, files in os.walk(path):
            for name in files:
                if name in ignore:
                    continue
                p = os.path.abspath(os.path.join(root, name))
                LOG.debug(f"Parsing file in {p}")
                yield from _index_grib_file(p, path_name=name)


class DirectorySource(IndexedSource):
    def __init__(self, path, **kwargs):
        self.path = path
        self.data_provider = None  # data_provider = reader?

        index = DirectoryIndex(
            index_location=os.path.join(os.path.abspath(path), "climetlab.index"),
            path=path,
        )

        super().__init__(index, **kwargs)

    def _set_selection(self, kwargs):
        fields = []
        for path, parts in self.index.get_path_offset_length(kwargs):
            for offset, length in parts:
                fields.append((path, offset, length))
        self.data_provider = FieldSet(fields=fields)


source = DirectorySource
