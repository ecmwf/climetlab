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

    def __init__(self, *arg):
        pass

    # @normalize('value', 'date', format='datetime.datetime')
    def normalize_datetime(self, value):
        return value.isoformat()

    def _to_json(self, entry):
        return json.dumps(entry)


class JsonStdoutDatabase(JsonDatabase):
    def load(self, iterator):
        count = 0
        for entry in iterator:
            entry = self.normalize(entry)
            print(self._to_json(entry))
            count += 1
        return count


class JsonFileDatabase(JsonDatabase):
    EXTENSION = ".json"

    def __init__(self, db_path):
        self.entries = []
        self.db_path = db_path
        if os.path.exists(db_path):
            with open(db_path) as f:
                for entry in f:
                    self.entries.append(json.loads(entry))

    def load(self, iterator):
        self.entries = []

        with open(self.db_path, "w") as f:
            for entry in iterator:
                entry = self.normalize(entry)
                self.entries.append(entry)
                print(self._to_json(entry), file=f)

        return len(self.entries)

    def lookup_parts(self, order=None, **kwargs):
        parts = []
        for e in self.entries:
            parts.append(Part(e["_path"], e["_offset"], e["_length"]))
        return Part.resolve(parts, os.path.dirname(self.db_path))

    def lookup_dicts(self):
        return self.entries
