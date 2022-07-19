# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import atexit
import functools
import os
import threading
import time
from collections import defaultdict
from contextlib import contextmanager

from climetlab.utils.humanize import number, seconds

PROFILING = int(os.environ.get("CLIMETLAB_PROFILING", 0))


@contextmanager
def timer(msg):
    start = time.time()
    print(f"{msg}: Starting.")
    try:
        yield None
    finally:
        print(f"{msg}: {time.time()-start}")


class C:
    n = 0
    now = 0
    elapsed = 0

    def start(self):
        self.n += 1
        if time is not None:
            self.now = time.time()

    def end(self):
        if time is not None:
            self.elapsed += time.time() - self.now

    def __repr__(self):
        m = self.n if self.n else 1
        return "calls: %s, elapsed: %s, average: %s" % (
            number(self.n),
            seconds(self.elapsed),
            seconds(self.elapsed / m),
        )


class Counter:
    def __init__(self, name):
        self.name = name
        self._c = C()
        self.threads = defaultdict(C)

    def __repr__(self):
        extra = ""
        if len(self.threads) > 1:
            extra = "\n threads:\n   %s" % (
                "\n   ".join(repr(t) for t in self.threads.values()),
            )
        return "COUNTER [%s], %s%s" % (
            self.name,
            self._c,
            extra,
        )

    def __enter__(self):
        if threading is not None:
            self._c.start()
            self.threads[threading.current_thread()].start()
            return self

    def __exit__(self, *args, **kwargs):
        if threading is not None:
            self._c.end()
            self.threads[threading.current_thread()].end()


COUNTERS = []


def print_counters():
    if PROFILING:
        for n in COUNTERS:
            print(n)


atexit.register(print_counters)


def call_counter(name=None):
    func = None
    if callable(name):
        func = name
        # TODO: Find the proper way of getting the
        # function full name.
        name = repr(func).split()[1]

    counter = Counter(name)
    COUNTERS.append(counter)

    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with counter:
                return func(*args, **kwargs)

        return wrapper

    if func is not None:
        return decorate(func)

    return decorate
