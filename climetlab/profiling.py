# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import atexit
import os
import time
from contextlib import contextmanager, wraps

from climetlab.utils.humanize import number, seconds

PROFILING = int(os.environ.get("CLIMETLAB_PROFILING", 0))


@contextmanager
def timer(msg):
    start = time.time()
    try:
        yield None
    finally:
        print(f"{msg}: {time.time()-start}")


class Counter:
    def __init__(self, name):
        self.name = name
        self.n = 0
        self.start = 0
        self.elapsed = 0

    def __repr__(self):
        m = self.n if self.n else 1
        return "COUNTER [%s], calls: %s, elapsed: %s, average: %s" % (
            self.name,
            number(self.n),
            seconds(self.elapsed),
            seconds(self.elapsed / m),
        )

    def __enter__(self):
        self.start = time.time()
        self.n += 1
        return self

    def __exit__(self, *args, **kwargs):
        self.elapsed += time.time() - self.start


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
        @wraps(func)
        def wrapper(*args, **kwargs):
            with counter:
                return func(*args, **kwargs)

        return wrapper

    if func is not None:
        return decorate(func)

    return decorate
