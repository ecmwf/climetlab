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

from climetlab import load_source
from climetlab.decorators import normalize
from climetlab.testing import climetlab_file


# def test_enum_definition():
@normalize("name", ("a", "b", "c"))
def enum_1(name="a"):
    return name


@normalize("name", ("a", "b", "c"))
def enum_no_default(name):
    return name


@normalize("name", ("a", "b", "c"))
def enum_default_is_none(name=None):
    return name


@normalize("name", (1, 0.5, 3))
def enum_number(name=1):
    return name


# def test_enum_list_definition():
@normalize("name", ["a", "b", "c"])
def enum_list_1(name="a"):
    return name


@normalize("name", ["a", "b", "c"])
def enum_list_no_default(name):
    return name


@normalize("name", ["a", "b", "c"])
def enum_list_default_is_none(name=None):
    return name


@normalize("name", ["a", "b", "c"])
def enum_list_default_is_all(name=ALL):
    return name


@normalize("name", [1, 0.5, 3])
def enum_list_number(name=1):
    return name


@normalize("a", [1, 2])
@normalize("b", [3, 4])
def enum_2_normalizers(a, b):
    return a


def test_enum_2_normalizers():
    enum_2_normalizers(a=1, b=4)
    # enum_2_normalizers(1,4)


def test_enum_decorator():
    assert enum_1("a") == "a"
    assert enum_1("b") == "b"
    assert enum_1() == "a"
    with pytest.raises(ValueError):
        enum_1("z")
    with pytest.raises(ValueError):
        enum_1(["a", "b"])


def test_enum_decorator_default():
    assert enum_no_default("a") == "a"
    assert enum_default_is_none("a") == "a"
    with pytest.raises(ValueError):
        enum_default_is_none()
    with pytest.raises(TypeError):
        enum_no_default()


def test_enum():

    enum_3 = normaliser(["a", "b", "c"], multiple=False)
    assert enum_3("a") == "a"
    assert enum_3("b") == "b"
    with pytest.raises(ValueError):
        enum_3("z")
    with pytest.raises(ValueError):
        enum_3(ALL)


def test_enum_list_decorator_default():
    assert enum_list_no_default("a") == ["a"]
    assert enum_list_default_is_none("a") == ["a"]
    assert enum_list_default_is_none() == ["a", "b", "c"]
    assert enum_list_default_is_all() == ["a", "b", "c"]
    assert enum_list_number(1.0) == [1]
    with pytest.raises(ValueError):
        enum_list_number("1")
    #    with pytest.raises(ValueError):
    #        enum_list_default_is_none()
    with pytest.raises(TypeError):
        enum_list_no_default()


def test_enum_list_case_sensitive():
    enum_5 = EnumNormaliser(["A", "b", "c"])
    assert enum_5(ALL) == ["A", "b", "c"]
    assert enum_5("a") == ["A"]
    assert enum_5("A") == ["A"]
    assert enum_5(["a", "B"]) == ["A", "b"]


@normalize(
    "name",
    ["a", "b", "c"],
    alias={
        "ab": ["a", "b"],
        "z": "a",
        "i": ["a", "b"],
        "j": "ab",
        "bad": ["a", "ab"],
    },
)
def enum_list_alias_1(name=1):
    return name


def test_enum_list_alias_1():
    assert enum_list_alias_1("a") == ["a"]
    assert enum_list_alias_1("b") == ["b"]
    assert enum_list_alias_1("ab") == ["a", "b"]
    assert enum_list_alias_1("z") == ["a"]
    assert enum_list_alias_1(["z", "b"]) == ["a", "b"]
    assert enum_list_alias_1("i") == ["a", "b"]
    assert enum_list_alias_1("j") == ["a", "b"]
    with pytest.raises(ValueError):
        enum_list_alias_1("bad")


@normalize(
    "name",
    [1, 2, 3],
    alias=lambda x: {"one": 1, "o": "one"}.get(x, x),
)
def enum_list_alias_2(name=1):
    return name


def test_enum_list_alias_2():
    assert enum_list_alias_2(1) == [1]
    assert enum_list_alias_2("one") == [1]
    assert enum_list_alias_2(["one"]) == [1]
    assert enum_list_alias_2(["o"]) == [1]


@normalize("name", ["a", "b", "c"], alias={"x": "y", "y": "z", "z": "a"})
def enum_alias(name=1):
    return name


def test_enum_alias():
    assert enum_alias("a") == ["a"]
    assert enum_alias("b") == ["b"]
    assert enum_alias("x") == ["a"]
    assert enum_alias("y") == ["a"]
    assert enum_alias("z") == ["a"]


if __name__ == "__main__":

    from climetlab.testing import main

    main(__file__)
