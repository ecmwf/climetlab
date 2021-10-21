#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import pytest
from test_availability import C1

from climetlab.decorators import availability, normalize
from climetlab.utils.availability import Availability

av_decorator = availability(C1)
av = Availability(C1)


@av_decorator
def func_a(level, param, step):
    return param


class Klass_a:
    @av_decorator
    def __init__(self, level, param, step):
        pass


class Klass_n:
    @normalize("param", ["a", "b", "c"])
    def __init__(self, level, param, step):
        pass


class Klass_a_n:
    @normalize("param", ["a", "b", "c"])
    @av_decorator
    def __init__(self, level, param, step):
        pass


class Klass_n_a:
    @av_decorator
    @normalize("param", ["a", "b", "c"])
    def __init__(self, level, param, step):
        pass


@normalize("param", ["a", "b", "c"])
def func_n(level, param, step):
    return param


@normalize("param", ["a", "b", "c"])
@av_decorator
def func_a_n(level, param, step):
    return param


@av_decorator
@normalize("param", ["a", "b", "c"])
def func_n_a(level, param, step):
    return param


@pytest.mark.parametrize(
    "func",
    [
        func_a,
        # func_n is excluded.
        func_n_a,
        # func_a_n, # TODO
        Klass_a,
        # Klass_n is excluded.
        Klass_n_a,
        # Klass_a_n, # TODO
    ],
)
def test_avail_1(func):
    func(level="1000", param="a", step="24")
    with pytest.raises(ValueError):
        func(level="1032100", param="a", step="24")


@pytest.mark.parametrize(
    "func",
    [func_n, Klass_n],
)
def test_avail_n(func):
    func(level="1000", param="a", step="24")
    func(level="1032100", param="a", step="24")


@pytest.mark.parametrize(
    "func",
    [
        func_a,
        func_n,
        func_n_a,
        # func_a_n,
        Klass_a,
        Klass_n,
        Klass_n_a,
        # Klass_a_n,
    ],
)
def test_norm(func):
    func(level="1000", param="a", step="24")

    with pytest.raises(ValueError):
        func(level="1000", param="zz", step="24")


def test_avail_norm_setup():
    @normalize("param", ["a", "b"])
    @availability(C1)
    def func1(param):
        return param

    with pytest.raises(ValueError):

        @normalize("param", ["unk1", "unk2"])
        @availability(C1)
        def func2(param):
            return param

    @normalize("param", ["a", "b"])
    @normalize("step", [24, 36])
    @normalize("param", ["A", "B"])
    def func3(param, step):
        return param

    assert func3("a", 24) == ["a"]

    with pytest.raises(ValueError):

        @normalize("param", ["A", "B"])
        @availability(C1)
        def func5(param, step):
            return param

    with pytest.raises(NotImplementedError):

        @av_decorator
        @normalize("param", ["a", "b"])
        @availability(C1)
        def func6(param, step):
            return param


def test_dev():
    func = Klass_a
    func(level="1000", param="a", step="24")


if __name__ == "__main__":
    # test_dev()
    from climetlab.testing import main

    main(__file__)
