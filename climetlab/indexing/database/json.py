# (C) Copyright 2021 ECMWF.
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

from climetlab.utils.parts import Part

from . import Database

LOG = logging.getLogger(__name__)

class JsonDatabase(Database):
    VERSION = 1
    EXTENSION = ".json"

    def __init__(self, db_path):
        self.entries = []
        self.db_path = db_path
        if os.path.exists(db_path):
            with open(db_path) as f:
                for entry in f:
                    self.entries.append(json.loads(entry))

    def load(self, iterator):
        self.entries = list(iterator)

        with open(self.db_path, "w") as f:
            for entry in self.entries:
                print(json.dumps(entry), file=f)

    def lookup(self, request, order=None, **kwargs):
        if request is None:
            return self.entries

        parts = []
        query = {
            k: set(v if isinstance(v, (list, tuple)) else [v])
            for k, v in request.items()
        }

        for e in self.entries:
            match = True
            for k, v in query.items():
                if e.get(k) not in v:
                    match = False
                    break
            if match:
                parts.append(Part(e["_path"], e["_offset"], e["_length"]))
        return Part.resolve(parts, os.path.dirname(self.db_path))
