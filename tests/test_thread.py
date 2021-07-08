#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import time
from datetime import datetime, timedelta

from climetlab.core.thread import SoftThreadPool


def test_thread():
    pool = SoftThreadPool()

    def f(x, t):
        time.sleep(t)
        return x * x

    start = datetime.now()

    futures = []
    futures.append(pool.submit(f, 0, 2))
    futures.append(pool.submit(f, 1, 2))
    futures.append(pool.submit(f, 2, 2))
    futures.append(pool.submit(f, 3, 1))

    duration = datetime.now() - start
    assert duration > timedelta(seconds=-0.000001)
    assert duration < timedelta(seconds=0.5)

    assert futures[3].result() == 9

    duration = datetime.now() - start
    assert duration > timedelta(seconds=0.5)
    assert duration < timedelta(seconds=1.5)

    assert futures[0].result() == 0

    duration = datetime.now() - start
    assert duration > timedelta(seconds=1.5)
    assert duration < timedelta(seconds=2.5)

    assert futures[0].result() == 0
    assert futures[1].result() == 1
    assert futures[2].result() == 4
    assert futures[3].result() == 9


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
