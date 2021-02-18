#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.decorators import parameters
import numpy as np
import datetime
from climetlab.utils.bbox import BoundingBox


@parameters(date="date-list")
def dates_1(date):
    print("date_1", date)
    return date


def test_dates():
    npdate = np.datetime64("2016-01-01")
    assert dates_1(date=npdate) == [datetime.datetime(2016, 1, 1)]


@parameters(area="bounding-box")
def bbox_1(ignore, area):
    return area


@parameters(area=("bounding-box", tuple))
def bbox_2(area, ignore=None):
    return area


@parameters(area=("bounding-box", list))
def bbox_3(area):
    return area


@parameters(area=("bounding-box", dict))
def bbox_4(area):
    return area


@parameters(area=("bounding-box"))
def bbox_5(area=[30.0, 2.0, 3.0, 4.0]):
    return area


def test_bbox():

    area = [30.0, 2.0, 3.0, 4.0]
    bbox = BoundingBox(north=30, west=2, south=3, east=4)

    assert bbox_1(None, area) == bbox
    assert bbox_1(area=area, ignore=None) == bbox

    assert bbox_2(area) == tuple(area)
    assert bbox_2(area=area) == tuple(area)

    assert bbox_3(area) == area

    assert bbox_4(area) == dict(north=30, west=2, south=3, east=4)

    assert bbox_5(area) == bbox


if __name__ == "__main__":
    test_dates()
    test_bbox()
