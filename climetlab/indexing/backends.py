# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import json
import os

from climetlab.utils import download_and_cache


class IndexBackend:
    pass


class JsonIndexBackend(IndexBackend):
    def __init__(self, filename):
        self._entries = None
        self.filename = filename

    @property
    def entries(self):
        if self._entries is not None:
            return self._entries

        self._entries = []

        if os.path.exists(self.filename):
            self.read_file_index(self.filename)
            return self._entries

        if self.filename.startswith("http://") or self.filename.startswith("https://"):
            path = download_and_cache(self.filename, update_if_out_of_date=True)
            self.read_file_index(path)
            return self._entries

        raise Exception(f"Cannot load index data from {self.filename}")

    def read_file_index(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
        for line in lines:
            entry = json.loads(line)
            self._entries.append(entry)

    def match(self, entry, request):
        for k, v in request.items():
            if isinstance(v, (tuple, list)):
                if not entry[k] in v:
                    return False
            else:
                if entry[k] != v:
                    return False
        return True

    def lookup(self, request):
        parts = []
        for e in self.entries:
            if self.match(e, request):
                path = e.get("_path", None)
                offset = int(e["_offset"])
                length = int(e["_length"])
                parts.append((path, [offset, length]))
        return parts
