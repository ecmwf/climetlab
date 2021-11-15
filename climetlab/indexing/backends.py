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


class JsonIndexBackend:
    def __init__(self):
        self._entries = None
        self.filename = None

    def add_index_file(self, filename):
        assert self.filename is None, (filename, self.filename)
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
            if entry[k] != v:
                return False
        return True

    def lookup(self, request):
        parts = []
        for e in self.entries:
            if self.match(e, request):
                part = (e["_path"], [e["_offset"], e["_length"]])
                parts.append(part)
        print(f"Build HTTP requests for {request}: {len(parts)} parts.")
        return parts
