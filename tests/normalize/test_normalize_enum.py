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

from climetlab import ALL
from climetlab.arguments.climetlab_types import EnumListType
from climetlab.arguments.climetlab_types import EnumType
from climetlab.decorators import normalize


def name_no_default(name):
    return name


def name_default_is_none(name=None):
    return name


def name_default_is_1(name=1):
    return name


def name_default_is_str_1(name="1"):
    return name


def name_default_is_str_a(name="a"):
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
    with pytest.raises(TypeError):
        g(a=1)


def test_enum_decorator():
    g = normalize("name", ("a", "b", "c"))(name_default_is_str_a)
    assert g("a") == "a"
    assert g("b") == "b"
    assert g() == "a"
    with pytest.raises(ValueError):
        g("z")
    assert g(["a", "b"]) == ["a", "b"]
    assert g(("a", "b")) == ("a", "b")
    assert g(["a"]) == ["a"]


def test_enum_multiple():
    g = normalize("name", ["a", "b", "c"], multiple=False)(name_default_is_str_a)
    with pytest.raises(TypeError):
        g(["a", "b"])


def test_enum_multiple_2():
    g = normalize("name", ["a", "b", "c"], multiple=True)(name_default_is_str_a)
    assert g(
        (
            "a",
            "b",
        )
    ) == ["a", "b"]


def test_enum_multiple_ALL_1():
    g = normalize("name", ["a", "b", "c"], multiple=False)(name_default_is_str_a)
    with pytest.raises(ValueError):
        g(ALL)


def test_enum_multiple_ALL_2():
    g = normalize("name", ["a", "b", "c"], multiple=True)(name_default_is_str_a)
    assert g(ALL) == ["a", "b", "c"]


def test_enum_float_1():
    g = normalize("name", [1, 0.5, 3], type=float, format="%03f")(name_default_is_1)
    assert g(1) == "1.000000"


@pytest.mark.skip("Not implemented. Need to discuss what it would mean.")
def test_enum_float_2():
    g = normalize("name", type=EnumListType([1, 0.5, 3]), format="%03f")(name_no_default)
    assert g(1) == ["1.000000"]

    g = normalize("name", type=EnumListType([1, 0.5, 3]), format="%03f", multiple=True)(name_no_default)
    assert g(1) == ["1.000000"]

    g = normalize("name", type=EnumListType([1, 0.5, 3]), format="%03f", multiple=False)(name_no_default)
    with pytest.raises(ValueError, match="Cannot .*"):
        assert g(1) == ["1.000000"]


@pytest.mark.skip("Not implemented. Need to discuss what it would mean.")
def test_enum_float_3():
    g = normalize("name", type=EnumType([1, 0.5, 3]), format="%03f")(name_no_default)
    assert g(1) == "1.000000"

    g = normalize("name", type=EnumType([1, 0.5, 3]), format="%03f", multiple=False)(name_no_default)
    assert g(1) == "1.000000"

    g = normalize("name", type=EnumType([1, 0.5, 3]), format="%03f", multiple=True)(name_no_default)
    with pytest.raises(ValueError, match="Cannot .*"):
        assert g(1) == ["1.000000"]


def test_enum_int_1():
    g = normalize("name", [1, 0.5, 3], type=int, multiple=True)(name_default_is_1)
    assert g(1) == [1]
    assert g(1.0) == [1]
    # assert g("1.0") == [1]
    assert g("1") == [1]
    assert g() == [1]


def test_enum_int_2():
    g = normalize("name", (1, 2, 3))(name_no_default)
    assert g("1") == 1
    assert g(1.0) == 1
    # assert g("1.0") == 1


def test_enum_int_3():
    g = normalize("name", [1, 2, 3], multiple=True)(name_no_default)
    assert g("1") == [1]
    assert g(1.0) == [1]
    # assert g("1.0") == [1]


def test_enum_float():
    g = normalize("name", (1.0, 0.5, 3.0))(name_no_default)
    assert g(1) == 1.0
    assert g("1") == 1.0


def test_enum_list_case_sensitive():
    g = normalize("name", ["A", "b", "c"], multiple=True)(name_no_default)
    # TODO:    assert g(ALL) == ["A", "b", "c"]
    assert g("a") == ["A"]
    assert g("A") == ["A"]
    assert g(["a", "B"]) == ["A", "b"]


def test_enum_list_alias_1():
    enum_list_alias_1 = normalize(
        "name",
        ["a", "b", "c"],
        multiple=True,
        aliases={
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
    # TODO: add more check for bad aliases in normalize
    # with pytest.raises(ValueError):
    #    enum_list_alias_1("bad")


def test_enum_list_alias_2():
    enum_list_alias_2 = normalize(
        "name",
        [1, 2, 3],
        multiple=True,
        aliases=lambda x: {"one": 1, "o": "one"}.get(x, x),
    )(name_no_default)
    assert enum_list_alias_2(1) == [1]
    assert enum_list_alias_2("one") == [1]
    assert enum_list_alias_2(["one"]) == [1]
    assert enum_list_alias_2(["o"]) == [1]


def test_enum_alias():
    enum_alias = normalize(
        "name",
        ["a", "b", "c"],
        multiple=True,
        aliases={"x": "y", "y": "z", "z": "a"},
    )(name_no_default)
    assert enum_alias("a") == ["a"]
    assert enum_alias("b") == ["b"]
    assert enum_alias("x") == ["a"]
    assert enum_alias("y") == ["a"]
    assert enum_alias("z") == ["a"]


def test_enum_none_1():
    @normalize(
        "name",
        ["a", "b", "c"],
        multiple=True,
        aliases={"x": "y", "y": "z", "z": "a"},
    )
    def enum_none(name):
        return name

    assert enum_none(None) is None


def test_enum_none_2():
    @normalize("name", ["a", "b", "c"], multiple=True, aliases={None: "b"})
    def enum_none_2(name):
        return name

    assert enum_none_2(None) == ["b"]


def test_enum_none_3():
    @normalize("name", ["a", "b", "c"], aliases={None: "b"})
    def enum_none_3(name):
        return name

    assert enum_none_3(None) == "b"


def test_enum_none_4():
    @normalize("name", ["a", "b", "c"], aliases={None: "b"})
    def enum_none_4(name=None):
        return name

    assert enum_none_4() == "b"


def test_enum_alias_2():
    enum_alias = normalize(
        "name",
        ["a", "b", "c"],
        aliases={"x": "y", "y": "z", "z": "a", "w": "wrong-value"},
    )(name_no_default)
    assert enum_alias("a") == "a"
    assert enum_alias("b") == "b"
    assert enum_alias("x") == "a"
    assert enum_alias("y") == "a"
    assert enum_alias("z") == "a"
    with pytest.raises(ValueError, match=".*wrong-value.*"):
        enum_alias("w")


def test_enum_default_1():
    @normalize(
        "name",
        ["a", "b", "c"],
    )
    def enum_default_1(name="wrong-default"):
        return name

    enum_default_1("a")
    with pytest.raises(ValueError, match=".*wrong-default.*"):
        enum_default_1()


def test_enum_aliases_from_file():
    enum_aliases_from_file = normalize(
        "name",
        ["a", "b", "c"],
        aliases="aliases.json",
    )(name_no_default)
    assert enum_aliases_from_file("y") == "b"
    with pytest.raises(ValueError):
        enum_aliases_from_file("unknown")


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
