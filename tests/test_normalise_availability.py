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

from climetlab.normalize import normalize_args
from climetlab.utils.availability import Availability, availability

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
    @normalize_args(param=["a", "b", "c"])
    def __init__(self, level, param, step):
        pass


class Klass_a_n:
    @normalize_args(param=["a", "b", "c"])
    @av_decorator
    def __init__(self, level, param, step):
        pass


class Klass_n_a:
    @av_decorator
    @normalize_args(param=["a", "b", "c"])
    def __init__(self, level, param, step):
        pass


class Klass_n_av:
    @normalize_args(param=["a", "b", "c"], _availability=av)
    def __init__(self, level, param, step):
        pass


@normalize_args(param=["a", "b", "c"], _availability=av)
class Klass_na:
    @av_decorator
    def __init__(self, level, param, step):
        pass


@normalize_args(param=["a", "b", "c"])
def func_n(level, param, step):
    return param


@normalize_args(param=["a", "b", "c"])
@av_decorator
def func_a_n(level, param, step):
    return param


@av_decorator
@normalize_args(param=["a", "b", "c"])
def func_n_a(level, param, step):
    return param


@normalize_args(param=["a", "b", "c"], _availability=av)
def func_n_av(level, param, step):
    return param


@pytest.mark.parametrize(
    "func",
    [
        func_a,
        # func_n is excluded.
        func_n_a,
        # func_a_n, # TODO
        func_n_av,
        Klass_a,
        # Klass_n is excluded.
        Klass_n_a,
        # Klass_a_n, # TODO
        Klass_n_av,
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
        func_n_av,
        Klass_a,
        Klass_n,
        Klass_n_a,
        # Klass_a_n,
        Klass_n_av,
    ],
)
def test_norm(func):
    func(level="1000", param="a", step="24")

    with pytest.raises(ValueError):
        func(level="1000", param="zz", step="24")


def test_dev():
    func_n_av(level="1000", param="a", step="24")
    # func_n_av(level="jkl", param="a", step="24")


@pytest.mark.skip("Not implemeted yet")
def test_avail_norm_setup():
    with pytest.raises(ValueError):

        @normalize_args(param=["x", "y"], _availability=av)
        def func_setup(level, param, step):
            return param


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
