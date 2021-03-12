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
from Magics.Magics import MagicsError

import climetlab as cml
from climetlab.utils.bbox import BoundingBox


def plot():
    bbox = BoundingBox(north=90, west=0, east=360, south=-90)
    cml.plot_map(bounding_box=bbox, projection="polar-north")


def test_exception():
    with pytest.raises(MagicsError):
        plot()


if __name__ == "__main__":
    plot()
