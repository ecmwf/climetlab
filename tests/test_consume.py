#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.utils import consume_args


def consume(func1, func2, *args, **kwargs):
    args_1, kwargs_1, args_2, kwargs_2 = consume_args(func1, *args, **kwargs)

    r1 = func1(*args_1, **kwargs_1)
    r2 = func2(*args_2, **kwargs_2)

    return r1, r2


def f_void():
    return 0


def f_x(x):
    assert x == 1
    return -x


def f_y(y):
    assert y == 2
    return 2 * y


def g_x(x=1, *, a=9):
    assert x == 1
    return -x + a


def g_y(y=2, *, b=9):
    assert y == 2
    return 2 * y + b


def test_consume():
    assert consume(f_void, f_void) == (0, 0)
    assert consume(f_void, f_x, 1) == (0, -1)
    assert consume(f_x, f_void, 1) == (-1, 0)
    assert consume(f_void, f_x, x=1) == (0, -1)
    assert consume(f_x, f_void, x=1) == (-1, 0)
    assert consume(f_x, f_y, 1, 2) == (-1, 4)
    assert consume(f_y, f_x, 2, 1) == (4, -1)
    assert consume(f_x, f_y, 1, y=2) == (-1, 4)
    assert consume(f_x, f_y, x=1, y=2) == (-1, 4)
    assert consume(f_y, f_x, x=1, y=2) == (4, -1)
    assert consume(g_y, g_x, 2, 1) == (13, 8)
    assert consume(g_y, g_x, 2, 1, a=5) == (13, 4)
    assert consume(g_y, g_x, 2, 1, b=5) == (9, 8)
    assert consume(g_y, g_x) == (13, 8)
    assert consume(g_y, g_x, b=5) == (9, 8)
    assert consume(g_y, g_x, y=2) == (13, 8)
    assert consume(g_y, g_x, y=2, a=6) == (13, 5)
    assert consume(g_y, g_x, x=1, a=6) == (13, 5)
    assert consume(g_y, g_x, x=1, b=4) == (8, 8)
    assert consume(g_y, g_x, y=2, b=4) == (8, 8)

    # Ambiguous use may not work as expected.
    # assert consume(f_y, g_y, y=2) == (4,13)
    # assert consume(g_y, f_y, 2, y=2) == (-1, 0)


if __name__ == "__main__":
    test_consume()
