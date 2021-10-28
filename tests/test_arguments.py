#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import sys

import numpy as np
import pytest

from climetlab import ALL, load_source
from climetlab.arguments import Argument, InputManager
from climetlab.decorators import _alias, _multiple, normalize
from climetlab.normalize import DateListNormaliser, EnumListNormaliser, EnumNormaliser
from climetlab.testing import climetlab_file
from climetlab.utils.bbox import BoundingBox


@pytest.fixture
def f():
    def func(a, b, c):
        return a, b, c

    return func


def test_deco_1(f):
    g = _multiple("a", multiple=True)(f)
    assert g(1, 2, 3) == ([1], 2, 3)
    assert f(1, 2, 3) == (1, 2, 3)


def test_deco_reuse_function(f):
    g = _multiple("a", multiple=True)(f)
    g = _multiple("a", multiple=True)(f)
    assert g(1, 2, 3) == ([1], 2, 3)


def test_deco_2(f):
    g = _alias("b", alias=dict(z=[1, 2, 3]))(f)
    assert g(1, "z", 3) == (1, [1, 2, 3], 3)


def test_argument_1():
    arg_a = Argument("a", multiple=False)
    arg_b = Argument("b", multiple=True, alias=dict(z=[1, 2, 3]))
    arg_c = Argument("c", values=("x", "y"))
    args = InputManager([arg_a, arg_c, arg_b])

    print(args.arguments)
    kwargs = dict(a="A", b="B", c="x")
    d = args.apply_to_kwargs(kwargs)
    assert d == dict(a="A", b=["B"], c="x"), d

    kwargs = dict(a="A", b="z", c="x")
    d = args.apply_to_kwargs(kwargs)
    assert d == dict(a="A", b=[1, 2, 3], c="x"), d


def test_argument_2():
    pass


def test_bad_decorator():
    arg_b = Argument("b", multiple=False, alias=dict(z=[1, 2, 3]))
    d = arg_b.apply_to_kwargs(dict(b=1))
    assert d == dict(b=1)

    d = arg_b.apply_to_kwargs(dict(b=["a"]))
    assert d == dict(b="a")


def test_deco_3(f):
    g = _multiple("a", multiple=True)(f)
    g = _multiple("a", multiple=True)(g)
    assert g(1, 2, 3) == ([1], 2, 3)
    assert f(1, 2, 3) == (1, 2, 3)


if __name__ == "__main__":
    # test_normalize_advanced_3()

    from climetlab.testing import main

    main(__file__)
