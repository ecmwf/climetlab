#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import sys

import pytest

from climetlab.arguments.args_kwargs import ArgsKwargs
from climetlab.decorators import normalize


def test_normalize_args_kwargs():
    def f(a, *args, x=1, **kwargs):
        return a, args, x, kwargs

    args = [1, 2]
    kwargs = dict(y="Y")
    ak = ArgsKwargs(args, kwargs, f)
    assert ak.positionals_only == []
    assert ak.defaults == {}
    ak.add_default_values_and_kwargs()
    assert ak.positionals_only == []
    assert ak.defaults == dict(x=1)


def test_normalize_kwargs_1():
    class Klass:
        @normalize("param", ["a", "b", "c"])
        def ok(self, param):
            pass

        @normalize("param", ["a", "b", "c"])
        def f(self, **kwargs):
            assert "param" in kwargs

    Klass().ok(param="a")

    Klass().f(param="a")


def test_normalize_kwargs_2():
    @normalize("date", "date-list")
    def f(**kwargs):
        pass

    f()


@pytest.mark.skipif(sys.version_info < (3, 8), reason="Python < 3.8")
def test_normalize_advanced_1():
    exec(
        """
# def f(a,/, b, c=4,*, x=3):
#    return a,b,c,x
# args = ['A']
# kwargs=dict(b=2, c=4)

@normalize("b", ["B", "BB"])
def f(a, /, b, c=4, *, x=3):
    return a, b, c, x

out = f("A", b="B", c=7, x=8)
assert out == ("A", "B", 7, 8), out
"""
    )


@pytest.mark.skipif(sys.version_info < (3, 8), reason="Python < 3.8")
def test_normalize_advanced_2():
    exec(
        """
@normalize("b", ["B", "BB"])
@normalize("a", ["A", "AA"])
def g(a, /, b, c=4, *, x=3):
    return a, b, c, x

out = g("A", b="B", c=7, x=8)
print(out)
assert out == ("A", "B", 7, 8), out
"""
    )


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
