#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from climetlab import load_source
from climetlab.decorators import normalize
from climetlab.testing import climetlab_file
from climetlab.utils.bbox import BoundingBox


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

    assert bbox_tuple("france") == (54.5, -6.0, 39.0, 9.5)
    assert bbox_tuple("verification.france") == (51.5, -5.0, 42.0, 8.5)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
