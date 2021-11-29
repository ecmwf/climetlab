# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import threading
import time

LOCK = threading.Lock()


class Statistics:
    def __init__(self, filename=None):
        self.collect = False
        self._current = {}
        self._events = []
        self._data = []

        if filename:
            self.load_from_json(filename)

    def append(self, event):
        self._events.append(event)
        self.process_event(event)

    def process_event(self, event):
        key = event[1]

        if key == "indexed-urls":
            assert not self._current, self._current

        for k, v in event[2].items():
            if k in self._current:
                assert self._current[k] == v
            self._current[k] = v

        if key == "transfer":  # last one
            for k in ["parts", "blocks"]:
                if k in self._current:
                    v = self._current[k]
                    # create nblocks and nparts
                    self._current["n" + k] = len(v)
                    # create size_blocks and size_parts
                    self._current["size_" + k] = sum(x[1] for x in v)
                    v = [(p[0], p[1]) for p in v]
                    v = json.dumps(v)
                    self._current[k] = v

            k = "method_args"
            if k in self._current:
                v = self._current[k]
                arg1 = 0.0
                if v:
                    arg1 = v[0]
                    try:
                        arg1 = float(arg1)
                    except Exception:
                        pass
                v = str(v)
                self._current["arg1"] = arg1
                self._current[k] = v

            self._data.append(self._current)
            self._current = {}

    def to_pandas(self):
        import pandas as pd

        return pd.DataFrame(self._data)

    def write_to_json(self, filename):
        import json

        with open(filename, "w") as f:
            json.dump(
                dict(events=self._events, data=self._data),
                f,
                indent=2,
            )

    def load_from_json(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
            self.process_event(data["events"])


global STATISTICS
STATISTICS = Statistics()


def collect_statistics(on):
    assert on in [True, False]
    with LOCK:
        global STATISTICS
        STATISTICS.collect = on


def reset_statistics():
    with LOCK:
        global STATISTICS
        STATISTICS = Statistics()


def record_statistics(name, **values):
    with LOCK:
        global STATISTICS
        if STATISTICS.collect:
            STATISTICS.append((time.time(), name, values))


def retrieve_statistics():
    with LOCK:
        global STATISTICS
        stats = STATISTICS
        STATISTICS = Statistics()
        return stats
