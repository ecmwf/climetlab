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

from climetlab.utils import bytes_to_string
from climetlab.utils.bbox import BoundingBox


def test_bytes():
    assert bytes_to_string(10) == "10"
    assert bytes_to_string(1024) == "1 KiB"
    assert bytes_to_string(1024 * 1024) == "1 MiB"


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
        assert bbox.width == 60, (bbox1, bbox2, bbox)

        bbox = bbox2.merge(bbox1)
        assert bbox.width == 60, (bbox1, bbox2, bbox)

    with pytest.raises(ValueError):
        BoundingBox(north=-10, west=0, south=30, east=1)

    with pytest.raises(ValueError):
        BoundingBox(north=90, west=1, south=30, east=1)
