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

from climetlab.decorators import normalize

# from climetlab.decorators import Normalizer # TODO: write it.


def test_normalize_kwargs():
    class Klass:
        @normalize("param", ["a", "b", "c"])
        def ok(self, param):
            pass

        @normalize("param", ["a", "b", "c"])
        def f(self, **kwargs):
            assert "param" in kwargs

    Klass().ok(param="a")

    Klass().f(param="a")


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
assert out == ("A", "B", 7, 8)
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
assert out == ("A", "B", 7, 8)
"""
    )


# @pytest.mark.skip(reason="Not implemented yet")
# def test_normalize_advanced_3():
#     out = Normalizer(values=("1", "2"), type=str, multiple=True)(1) == ["1"]
#     assert Normalizer(values=("1", "2"), type=str, multiple=True)((1, 2)) == ["1", "2"]

#     assert Normalizer(values=("1", "2"), type=int, multiple=True)(1) == [1]
#     assert Normalizer(values=("1", "2"), type=int, multiple=True)(1.0) == [1]


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
