# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import json


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

        with open(self.filename, "r") as f:
            lines = f.readlines()
        self._entries = []
        for line in lines:
            entry = json.loads(line)
            self.entries.append(entry)

        assert isinstance(self._entries, (list, tuple)), self._entries

        return self._entries

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
        print(f"Build HTTP requests for {request}: {len(parts)} parts.")
        return parts
