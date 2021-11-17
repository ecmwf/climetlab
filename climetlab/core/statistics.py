# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import threading
import time

LOCK = threading.Lock()
COLLECT = False
STATISTICS = []


def collect_statistics(on):
    with LOCK:
        global COLLECT, STATISTICS
        COLLECT = on
        STATISTICS = []


def reset_statistics():
    with LOCK:
        global STATISTICS
        STATISTICS = []


def record_statistics(name, **values):
    with LOCK:
        if COLLECT:
            STATISTICS.append((time.time(), name, values))


def retrieve_statistics():
    with LOCK:
        global STATISTICS
        stats = STATISTICS
        STATISTICS = []
        return stats
