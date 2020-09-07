#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.utils import bytes_to_string
from climetlab.core.bbox import BoundingBox


def test_bytes():
    assert bytes_to_string(10) == "10"
    assert bytes_to_string(1024) == "1 KiB"
    assert bytes_to_string(1024 * 1024) == "1 MiB"


def test_bbox():

    for i in range(-365, 365):
        bbox = BoundingBox(90, i, 30, 10 + i)
        assert bbox.width == 10, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(90, i, 30, 350 + i)
        assert bbox.width == 350, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(90, i, 30, (10 + i) % 360)
        assert bbox.width == 10, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(90, i, 30, (350 + i) % 360)
        assert bbox.width == 350, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(90, i % 360, 30, 10 + i)
        assert bbox.width == 10, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(90, i % 360, 30, 350 + i)
        assert bbox.width == 350, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(90, i % 360, 30, (10 + i) % 360)
        assert bbox.width == 10, bbox

    for i in range(-365, 365):
        bbox = BoundingBox(90, i % 360, 30, (350 + i) % 360)
        assert bbox.width == 350, bbox

    for i in range(-365, 365):
        bbox1 = BoundingBox(90, 150 + i, 30, 170 + i)
        bbox2 = BoundingBox(90, -170 + i, 30, -150 + i)
        bbox = bbox1.merge(bbox2)
        assert bbox.width == 60, (bbox1, bbox2, bbox)

        bbox = bbox2.merge(bbox1)
        assert bbox.width == 60, (bbox1, bbox2, bbox)
