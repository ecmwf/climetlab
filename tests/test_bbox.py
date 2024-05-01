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


def test_globe():
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

    b1 = BoundingBox(north=90, west=-180, east=0, south=-90)
    b2 = BoundingBox(north=90, west=0, east=180, south=-90)
    b0 = b1.merge(b2)
    assert b0.width == 360


def test_almost_globe():
    globe1 = BoundingBox(north=90, west=1, east=360, south=-90)

    globe2 = BoundingBox(north=90, west=-180, east=179, south=-90)

    assert globe1.merge(globe2).width == 360, globe1.merge(globe2).width
    assert globe2.merge(globe1).width == 360, globe2.merge(globe1).width
    print(globe1.merge(globe2))

    # assert globe1.merge(globe2) == globe1,globe1.merge(globe2)
    # assert globe2.merge(globe1) == globe2, globe2.merge(globe1)


def test_bbox():
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

        merge1 = bbox1.merge(bbox2)
        merge2 = bbox2.merge(bbox1)
        assert merge1 == merge2, (bbox1, bbox2, merge1, merge2)

    with pytest.raises(ValueError):
        BoundingBox(north=-10, west=0, south=30, east=1)

    b0 = BoundingBox(north=89.9746, west=-179.975, south=-89.9746, east=179.975)
    b1 = BoundingBox(north=89.9746, west=-179.975, south=-89.9746, east=179.975)
    b2 = BoundingBox(north=89.9746, west=-179.975, south=-89.9746, east=179.975)
    b3 = b1.merge(b2)

    assert b0 == b3


def test_overlapping_bbox_1():
    for offset in range(-500, 500, 10):
        one = BoundingBox(north=90, west=offset + 10, east=offset + 20, south=-90)
        two = BoundingBox(north=90, west=offset + 40, east=offset + 60, south=-90)
        three = BoundingBox(north=90, west=offset + 15, east=offset + 35, south=-90)

        sets = []
        sets.append([one, two, three])
        sets.append([two, one, three])
        sets.append([one, three, two])
        sets.append([one, three, two, one, three])
        sets.append([one, one, one, two, one, two, one, three])
        for i, s in enumerate(sets):
            merged = BoundingBox.multi_merge(s)
            expected = BoundingBox(east=offset + 60, west=offset + 10, north=90, south=-90)
            assert merged.east == expected.east, (
                i,
                merged.east,
                expected.east,
                merged,
                s,
            )
            assert merged.west == expected.west, (
                i,
                merged.west,
                expected.west,
                merged,
                s,
            )

        four = BoundingBox(north=90, west=offset - 200, east=offset + 10, south=-90)
        sets = []
        sets.append([one, two, three, four])
        sets.append([two, one, four, three])
        sets.append([one, three, four, two])
        sets.append([one, three, two, four, one, three])
        sets.append([one, one, one, two, four, one, two, one, three])
        for i, s in enumerate(sets):
            merged = BoundingBox.multi_merge(s)
            expected = BoundingBox(east=offset + 60, west=offset - 200, north=90, south=-90)
            assert merged.east % 360 == expected.east % 360, (
                i,
                offset,
                merged.east,
                expected.east,
                merged,
                s,
            )
            assert merged.west % 360 == expected.west % 360, (
                i,
                merged.west,
                expected.west,
                merged,
                s,
            )
            assert merged.west < merged.east


def xxxtest_overlaps():
    b1 = BoundingBox(north=90, west=-200, south=-90, east=-130)
    b2 = BoundingBox(north=90, west=-180, south=-90, east=-90)
    b0 = b1.overlaps(b2)
    assert b0


def test_overlapping_bbox_2():
    b1 = BoundingBox(north=90, west=-200, south=-90, east=-130)
    b2 = BoundingBox(north=90, west=-180, south=-90, east=-90)
    b0 = b1.merge(b2)

    assert b0.width == 110, b0.width

    b3 = BoundingBox(north=90, west=-210, south=-90, east=-160)
    b0 = b0.merge(b3)
    assert b0.width == 120, b0.width

    #      ----------------------
    #           ---------------------
    # ---------------------

    for i in range(-365, 365):
        b1 = BoundingBox(north=90, west=10 + i, south=-90, east=80 + i)
        b2 = BoundingBox(north=90, west=30 + i, south=-90, east=120 + i)
        b3 = BoundingBox(north=90, west=0 + i, south=-90, east=50 + i)
        b0 = BoundingBox.multi_merge([b1, b2, b3])
        assert b0.width == 120, (b0.width, b0)

    # --------------------------------
    #           ---------------------
    #     ---------------------

    for i in range(-365, 365):
        b1 = BoundingBox(north=90, west=-10 + i, south=-90, east=200 + i)
        b2 = BoundingBox(north=90, west=30 + i, south=-90, east=120 + i)
        b3 = BoundingBox(north=90, west=0 + i, south=-90, east=50 + i)

        b0 = BoundingBox.multi_merge([b1, b2, b3])
        assert b0.width == 210, (b0.width, b0)

    # --------------------------------
    #           --------------------------
    #     ---------------------

    for i in range(-365, 365):
        b1 = BoundingBox(north=90, west=-10 + i, south=-90, east=200 + i)
        b2 = BoundingBox(north=90, west=30 + i, south=-90, east=300 + i)
        b3 = BoundingBox(north=90, west=0 + i, south=-90, east=50 + i)

        b0 = BoundingBox.multi_merge([b1, b2, b3])

        assert b0.width == 310, (b0.width, b0)


def test_overlapping_bbox_3():
    for i in range(361):
        b1 = BoundingBox(north=90, west=-45 - i, south=-90, east=45 - i)
        b2 = BoundingBox(north=90, west=-45 + i, south=-90, east=45 + i)
        b0 = b1.merge(b2)

        if i <= 90:
            assert b0.width == 90 + 2 * i, (i, b0.width, b0)

        if i > 90 and i <= 180:
            assert b0.width == 3 * 90 - 2 * (i - 90), (i, b0.width, b0)

        if i > 180 and i <= 270:
            assert b0.width == 90 + 2 * (i - 180), (i, b0.width, b0)

        if i > 270:
            assert b0.width == 3 * 90 - 2 * (i - 270), (i, b0.width, b0)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
