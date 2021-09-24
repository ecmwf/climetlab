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

from climetlab.utils.bbox import BoundingBox


def test_bbox():

    globe1 = BoundingBox(north=90, west=0, east=360, south=-90)
    assert globe1.width == 360
    assert globe1.west == 0

    globe2 = BoundingBox(north=90, west=-180, east=180, south=-90)
    assert globe2.width == 360
    assert globe2.west == -180

    assert globe1.merge(globe2).width == 360, globe1.merge(globe2).width
    assert globe2.merge(globe1).width == 360, globe2.merge(globe1).width


    # assert globe1.merge(globe2) == globe1,globe1.merge(globe2)
    # assert globe2.merge(globe1) == globe2, globe2.merge(globe1)

    for i in range(-365, 365):
        bbox = BoundingBox(north=90, west=i, south=30, east=10 + i)
        assert bbox.width == 10, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(north=90, west=i, south=30, east=350 + i)
        assert bbox.width == 350, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(north=90, west=i, south=30, east=(10 + i) % 360)
        assert bbox.width == 10, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(north=90, west=i, south=30, east=(350 + i) % 360)
        assert bbox.width == 350, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(north=90, west=i % 360, south=30, east=10 + i)
        assert bbox.width == 10, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(north=90, west=i % 360, south=30, east=350 + i)
        assert bbox.width == 350, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(north=90, west=i % 360, south=30, east=(10 + i) % 360)
        assert bbox.width == 10, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(north=90, west=i % 360, south=30, east=(350 + i) % 360)
        assert bbox.width == 350, bbox

    for i in range(-365, 365):
        bbox1 = BoundingBox(north=90, west=150 + i, south=30, east=170 + i)
        bbox2 = BoundingBox(north=90, west=-170 + i, south=30, east=-150 + i)

        bbox = bbox1.merge(bbox2)
        assert bbox.width == 60, (bbox1, bbox2, bbox, bbox.width)

        bbox = bbox2.merge(bbox1)
        assert bbox.width == 60, (bbox1, bbox2, bbox, bbox.width)

        assert bbox1.merge(bbox2) == bbox2.merge(bbox1)

    with pytest.raises(ValueError):
        BoundingBox(north=-10, west=0, south=30, east=1)

    b0 = BoundingBox(north=89.9746, west=-179.975, south=-89.9746, east=179.975)
    b1 = BoundingBox(north=89.9746, west=-179.975, south=-89.9746, east=179.975)
    b2 = BoundingBox(north=89.9746, west=-179.975, south=-89.9746, east=179.975)
    b3 = b1.merge(b2)
    assert b0 == b1
    for a, b in zip(b3.as_tuple(), b0.as_tuple()):
        assert abs(a-b)<1e-14, (a,b,a-b)
        print(a, b, abs(a-b)<1e-14)



if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
