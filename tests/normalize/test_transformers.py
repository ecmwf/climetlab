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

from climetlab.arguments.climetlab_types import (
    BoundingBoxType,
    DateType,
    FloatType,
    IntType,
)
from climetlab.arguments.transformers import FormatTransformer
from climetlab.utils.bbox import BoundingBox


def test_format():
    assert (
        FormatTransformer("noname", DateType, format="%Y:%m:%d").transform(
            datetime.datetime(2020, 1, 1)
        )
        == "2020:01:01"
    )
    assert FormatTransformer("noname", IntType, format="%04d").transform(42) == "0042"
    assert (
        FormatTransformer("noname", FloatType, format="%.1f").transform(3.14) == "3.1"
    )
    b1 = BoundingBox(north=90, west=-45, south=-90, east=45)
    assert FormatTransformer("noname", BoundingBoxType, format=tuple).transform(b1) == (
        90.0,
        -45.0,
        -90.0,
        45.0,
    )
    assert FormatTransformer("noname", BoundingBoxType, format="dict").transform(
        b1
    ) == {"east": 45.0, "north": 90.0, "south": -90.0, "west": -45.0}
    assert FormatTransformer("noname", BoundingBoxType, format=list).transform(b1) == [
        90.0,
        -45.0,
        -90.0,
        45.0,
    ]


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
