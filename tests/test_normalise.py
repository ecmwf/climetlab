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

import numpy as np
import pytest

from climetlab import load_source
from climetlab.normalize import EnumNormaliser, normalize_args
from climetlab.utils.bbox import BoundingBox


@normalize_args(parameter=("variable-list(mars)"))
def values_mars(parameter):
    return parameter


@normalize_args(parameter=("variable-list(cf)"))
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


@normalize_args(date="date-list")
def dates_1(date):
    return date


def test_dates():
    npdate = np.datetime64("2016-01-01")
    assert dates_1(date=npdate) == [datetime.datetime(2016, 1, 1)]

    source = load_source("file", "docs/examples/test.grib")
    assert dates_1(source[0]) == [datetime.datetime(2020, 5, 13, 12, 0)]

    source = load_source("file", "docs/examples/test.nc")

    #  For now
    with pytest.raises(NotImplementedError):
        assert dates_1(source[0]) == [datetime.datetime(2020, 5, 13, 12, 0)]


@normalize_args(area="bounding-box")
def bbox_list(ignore, area):
    return area


@normalize_args(area="bounding-box(tuple)")
def bbox_tuple(area, ignore=None):
    return area


@normalize_args(area="bounding-box(list)")
def bbox_bbox(area):
    return area


@normalize_args(area="bounding-box(dict)")
def bbox_dict(area):
    return area


@normalize_args(area="bounding-box")
def bbox_defaults(area=None):
    return area


@normalize_args(name=["a", "b", "c"])
def enum_1(name=None):
    return name


@normalize_args(name=[1, 0.5, 3])
def enum_2(name=1):
    return name


def test_enum_decorator():
    assert enum_1("a") == "a"
    assert enum_1("b") == "b"
    with pytest.raises(ValueError):
        enum_1("z")
    assert enum_1(["a", "b"]) == ["a", "b"]
    with pytest.raises(ValueError):
        enum_1(1)


def test_enum_none():
    assert enum_1() == ["a", "b", "c"]
    assert enum_1(None) == ["a", "b", "c"]


def test_enum():
    enum_3 = EnumNormaliser(["a", "b", "c"])
    assert enum_3("a") == "a"
    assert enum_3("b") == "b"
    with pytest.raises(ValueError):
        enum_3("z")
    assert enum_3(None) == ["a", "b", "c"]


def test_enum_case_sensitive():
    enum_4 = EnumNormaliser(["A", "b", "c"], case_sensitive=True)
    enum_5 = EnumNormaliser(["A", "b", "c"], case_sensitive=False)
    assert enum_4(None) == ["A", "b", "c"]
    assert enum_5(None) == ["A", "b", "c"]
    assert enum_4("A") == "A"
    assert enum_5("a") == "A"
    with pytest.raises(ValueError):
        enum_4("a")
    assert enum_5("A") == "A"
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

    source = load_source("file", "docs/examples/test.grib")
    assert bbox_tuple(source[0]) == (73.0, -27.0, 33.0, 45.0)

    source = load_source("file", "docs/examples/test.nc")
    assert bbox_tuple(source[0]) == (73.0, -27.0, 33.0, 45.0)


if __name__ == "__main__":
    for k, f in sorted(globals().items()):
        if k.startswith("test_") and callable(f):
            print(k)
            f()
