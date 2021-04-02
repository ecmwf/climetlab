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
from climetlab.normalize import normalize_args
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
    test_dates()
    test_bbox()
    test_param_convention_cf()
    test_param_convention_mars()
