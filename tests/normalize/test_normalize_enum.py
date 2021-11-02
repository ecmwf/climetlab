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
from typing import MutableMapping

import numpy as np
import pytest

from climetlab import ALL, load_source
from climetlab.decorators import normalize
from climetlab.testing import climetlab_file


def name_no_default(name):
    return name


def name_default_is_none(name=None):
    return name


def name_default_is_1(name=1):
    return name


def name_default_is_str_1(name="1"):
    return name


def name_default_is_str_a(name="1"):
    return name


def name_default_is_all(name=ALL):
    return name


def a_b_no_default(a, b):
    return a, b


def test_enum_2_normalizers():
    g = a_b_no_default
    g = normalize("a", [1, 2])(g)
    g = normalize("b", [3, 4])(g)
    assert g(a=1, b=4) == (1, 4)
    with pytest.raises(ValueError):
        g(a=1)


def test_enum_decorator():
    g = normalize("name", ("a", "b", "c"))(name_default_is_str_a)
    assert g("a") == "a"
    assert g("b") == "b"
    assert g() == "a"
    with pytest.raises(ValueError):
        g("z")
    with pytest.raises(ValueError):
        g(["a", "b"])


def test_enum_multiple():
    g = normalize("name", ["a", "b", "c"], multiple=False)(name_default_is_str_a)
    with pytest.raises(ValueError):
        g(["a", "b"])
    with pytest.raises(ValueError):
        g(ALL)

    g = normalize("name", ["a", "b", "c"], multiple=True)(name_default_is_str_a)
    assert (
        g(
            (
                "a",
                "b",
            )
        )
        == ["a", "b"]
    )
    assert g(ALL) == ["a", "b", "c"]


def test_enum_int():
    g = normalize("name", [1, 0.5, 3], type=int, multiple=True)(name_default_is_1)
    assert g(1) == [1]
    assert g(1.0) == [1]
    assert g("1.0") == [1]
    assert g("1") == [1]
    assert g() == [1]

    g = normalize("name", (1, 0.5, 3))(name_no_default)
    assert g(1) == 1
    assert g("1") == 1

    g = normalize("name", [1, 0.5, 3], multiple=True)(name_no_default)
    assert g("1") == 1
    assert g("1.0") == [1]


def test_enum_list_case_sensitive():
    g = normalize("name", ["A", "b", "c"], multiple=True)(name_no_default)
    assert g(ALL) == ["A", "b", "c"]
    assert g("a") == ["A"]
    assert g("A") == ["A"]
    assert g(["a", "B"]) == ["A", "b"]


def test_enum_list_alias_1():
    enum_list_alias_1 = normalize(
        "name",
        ["a", "b", "c"],
        alias={
            "ab": ["a", "b"],
            "z": "a",
            "i": ["a", "b"],
            "j": "ab",
            "bad": ["a", "ab"],
        },
    )(name_no_default)
    assert enum_list_alias_1("a") == ["a"]
    assert enum_list_alias_1("b") == ["b"]
    assert enum_list_alias_1("ab") == ["a", "b"]
    assert enum_list_alias_1("z") == ["a"]
    assert enum_list_alias_1(["z", "b"]) == ["a", "b"]
    assert enum_list_alias_1("i") == ["a", "b"]
    assert enum_list_alias_1("j") == ["a", "b"]
    with pytest.raises(ValueError):
        enum_list_alias_1("bad")


def test_enum_list_alias_2():
    enum_list_alias_2 = normalize(
        "name",
        [1, 2, 3],
        alias=lambda x: {"one": 1, "o": "one"}.get(x, x),
    )(name_no_default)
    assert enum_list_alias_2(1) == [1]
    assert enum_list_alias_2("one") == [1]
    assert enum_list_alias_2(["one"]) == [1]
    assert enum_list_alias_2(["o"]) == [1]


def test_enum_alias():
    enum_alias = normalize(
        "name",
        ["a", "b", "c"],
        alias={"x": "y", "y": "z", "z": "a"},
    )(name_no_default)
    assert enum_alias("a") == ["a"]
    assert enum_alias("b") == ["b"]
    assert enum_alias("x") == ["a"]
    assert enum_alias("y") == ["a"]
    assert enum_alias("z") == ["a"]


if __name__ == "__main__":

    from climetlab.testing import main

    main(__file__)
