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
from climetlab.decorators import normalize
from climetlab.normalize import DateListNormaliser, EnumListNormaliser, EnumNormaliser
from climetlab.testing import climetlab_file
from climetlab.utils.bbox import BoundingBox


@normalize("parameter", ("variable-list(mars)"))
def values_mars(parameter):
    return parameter


@normalize("parameter", ("variable-list(cf)"))
def values_cf(parameter):
    return parameter


def test_param_convention_mars():
    assert values_mars(parameter="tp") == "tp"
    assert values_mars(parameter="2t") == "2t"
    assert values_mars(parameter="t2m") == "2t"
    assert values_mars(parameter=["t2m", "tp"]) == ["2t", "tp"]
    assert values_mars(parameter="whatever") == "whatever"


def test_param_convention_cf():
    assert values_cf(parameter="tp") == "tp"
    assert values_cf(parameter="2t") == "t2m"
    assert values_cf(parameter="t2m") == "t2m"


@normalize("date", "date")
def dates_1(date):
    return date


@normalize("date", "date-list")
def dates_list_1(date):
    return date


def test_dates():
    npdate = np.datetime64("2016-01-01")
    assert dates_1(date=npdate) == datetime.datetime(2016, 1, 1)
    assert dates_list_1(date=npdate) == [datetime.datetime(2016, 1, 1)]

    source = load_source("file", climetlab_file("docs/examples/test.grib"))
    assert dates_1(source[0]) == datetime.datetime(2020, 5, 13, 12, 0)
    assert dates_list_1(source[0]) == [datetime.datetime(2020, 5, 13, 12, 0)]

    source = load_source("file", climetlab_file("docs/examples/test.nc"))

    #  For now
    with pytest.raises(NotImplementedError):
        assert dates_1(source[0]) == datetime.datetime(2020, 5, 13, 12, 0)
        assert dates_list_1(source[0]) == [datetime.datetime(2020, 5, 13, 12, 0)]


def test_dates_no_list():
    norm = DateListNormaliser("%Y.%m.%d")
    assert norm("20200513") == ["2020.05.13"]
    assert norm([datetime.datetime(2020, 5, 13, 0, 0)]) == ["2020.05.13"]
    assert norm([datetime.datetime(2020, 5, 13, 23, 59)]) == ["2020.05.13"]


# def test_dates_with_list():
#     norm = DateListNormaliser("%Y.%m.%d", valid=["2020.05.13"] )
#     assert norm("20200513") == ["2020.05.13"]
#     assert norm([datetime.datetime(2020, 5, 13, 12, 0)]) == ["2020.05.13"]
#
#     with pytest.raises(ValueError):
#         assert norm("19991231")


def test_dates_3():
    norm = DateListNormaliser()
    assert norm("20200513") == [datetime.datetime(2020, 5, 13, 0, 0)]
    assert norm([datetime.datetime(2020, 5, 13, 0, 0)]) == [
        datetime.datetime(2020, 5, 13, 0, 0)
    ]


@normalize("area", "bounding-box")
def bbox_list(ignore, area):
    return area


@normalize("area", "bounding-box(tuple)")
def bbox_tuple(area, ignore=None):
    return area


@normalize("area", "bounding-box(list)")
def bbox_bbox(area):
    return area


@normalize("area", "bounding-box(dict)")
def bbox_dict(area):
    return area


@normalize("area", "bounding-box")
def bbox_defaults(area=None):
    return area


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


#    for k, v in vars().items():
#         globals()[k] = v


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


# for k, v in vars().items():
#    globals()[k] = v


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
    enum_3 = EnumNormaliser(["a", "b", "c"])
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
    enum_5 = EnumListNormaliser(["A", "b", "c"])
    assert enum_5(ALL) == ["A", "b", "c"]
    assert enum_5("a") == ["A"]
    assert enum_5("A") == ["A"]
    assert enum_5(["a", "B"]) == ["A", "b"]


def test_bbox():

    area = [30.0, 2.0, 3.0, 4.0]
    bbox = BoundingBox(north=30, west=2, south=3, east=4)

    assert bbox_list(None, area) == bbox
    assert bbox_list(area=area, ignore=None) == bbox

    assert bbox_tuple(area) == tuple(area)
    assert bbox_tuple(area=area) == tuple(area)

    assert bbox_bbox(area) == area

    assert bbox_dict(area) == dict(north=30, west=2, south=3, east=4)

    assert bbox_defaults(area) == bbox

    source = load_source("file", climetlab_file("docs/examples/test.grib"))
    assert bbox_tuple(source[0]) == (73.0, -27.0, 33.0, 45.0)

    source = load_source("file", climetlab_file("docs/examples/test.nc"))
    assert bbox_tuple(source[0]) == (73.0, -27.0, 33.0, 45.0)


def test_normalize_kwargs():
    class Klass:
        @normalize("param", ["a", "b", "c"])
        def ok(self, param):
            pass

        @normalize("param", ["a", "b", "c"])
        def f(self, **kwargs):
            # def f(self, param, **kwargs):
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
assert out == ("A", ["B"], 7, 8)
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
assert out == (["A"], ["B"], 7, 8)
"""
    )


def test_normalize_advanced_3():
    from climetlab.arguments import normaliser

    assert normaliser(("1", "2"), type=str, multiple=True)(1) == ["1"]
    assert normaliser(("1", "2"), type=str, multiple=True)((1, 2)) == ["1", "2"]


#    assert normaliser((1, 2), type=int, multiple=True)(1) == [1]

if __name__ == "__main__":
    # test_normalize_advanced_3()

    from climetlab.testing import main

    main(__file__)
