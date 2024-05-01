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

import pytest

from climetlab.arguments.climetlab_types import BoundingBoxType
from climetlab.arguments.climetlab_types import DateListType
from climetlab.arguments.climetlab_types import DateType
from climetlab.arguments.climetlab_types import EnumListType
from climetlab.arguments.climetlab_types import EnumType
from climetlab.arguments.climetlab_types import FloatListType
from climetlab.arguments.climetlab_types import FloatType
from climetlab.arguments.climetlab_types import IntListType
from climetlab.arguments.climetlab_types import IntType
from climetlab.arguments.climetlab_types import StrListType
from climetlab.arguments.climetlab_types import StrType
from climetlab.arguments.climetlab_types import VariableListType
from climetlab.arguments.climetlab_types import VariableType
from climetlab.arguments.transformers import FormatTransformer
from climetlab.arguments.transformers import TypeTransformer
from climetlab.utils.bbox import BoundingBox

enum = ("a", "b", "c")


def test_types():
    assert TypeTransformer(None, type=EnumType(enum)).transform("a") == "a"

    assert TypeTransformer(None, type=EnumListType(enum)).transform("a") == ["a"]

    assert TypeTransformer(None, type=StrType).transform(42) == "42"
    assert TypeTransformer(None, type=StrListType).transform(42) == ["42"]

    assert TypeTransformer(None, type=IntType).transform("42") == 42
    assert TypeTransformer(None, type=IntListType).transform("42") == [42]
    assert TypeTransformer(None, type=IntListType).transform("42/to/44") == [42, 43, 44]
    assert TypeTransformer(None, type=IntListType).transform("42/to/48/by/3") == [
        42,
        45,
        48,
    ]

    assert TypeTransformer(None, type=FloatType).transform("3.14") == 3.14
    assert TypeTransformer(None, type=FloatListType).transform(3.14) == [3.14]

    assert TypeTransformer(None, type=DateType).transform(20000101) == datetime.datetime(2000, 1, 1)

    assert TypeTransformer(None, type=DateListType).transform("20000101/to/20000103") == [
        datetime.datetime(2000, 1, 1),
        datetime.datetime(2000, 1, 2),
        datetime.datetime(2000, 1, 3),
    ]

    assert TypeTransformer(None, type=DateListType).transform((20000101, 20000102, 20000103)) == [
        datetime.datetime(2000, 1, 1),
        datetime.datetime(2000, 1, 2),
        datetime.datetime(2000, 1, 3),
    ]

    with pytest.raises(AssertionError):  # FIXME: Not sure what this should be
        assert TypeTransformer(None, type=VariableType("cf")).transform(42) == 0

    with pytest.raises(AssertionError):  # FIXME: Not sure what this should be
        assert TypeTransformer(None, type=VariableListType("cf")).transform(42) == 0

    assert TypeTransformer(None, type=BoundingBoxType).transform((1, -1, -1, 1)) == BoundingBox(
        north=1, west=-1, south=-1, east=1
    )


def test_formats():
    assert FormatTransformer(None, type=EnumType(enum), format="%4s").transform("a") == "   a"

    assert FormatTransformer(None, type=EnumListType(enum), format="%4s").transform(("a", "b")) == ["   a", "   b"]

    assert FormatTransformer(None, type=StrType, format="%4s").transform("a") == "   a"

    assert FormatTransformer(None, type=StrListType, format="%4s").transform(("a", "b")) == ["   a", "   b"]

    assert FormatTransformer(None, type=IntType, format="%04d").transform(42) == "0042"

    assert FormatTransformer(None, type=IntListType, format="%04d").transform((42, 43)) == ["0042", "0043"]

    assert FormatTransformer(None, type=FloatType, format="%4s").transform("3.14") == "3.14"

    assert FormatTransformer(None, type=FloatType, format="%.1f").transform(3.14) == "3.1"

    assert FormatTransformer(None, type=FloatListType, format="%.1f").transform((3.14, 2.72)) == ["3.1", "2.7"]

    assert FormatTransformer(None, type=DateType, format="%Y").transform(datetime.datetime(2000, 1, 1)) == "2000"

    assert FormatTransformer(None, type=DateListType, format="%d").transform(
        (datetime.datetime(2000, 1, 1), datetime.datetime(2000, 1, 2))
    ) == ["01", "02"]

    with pytest.raises(Exception):  # FIXME: Not sure what this should be
        assert FormatTransformer(None, type=VariableType, format="%4s").transform(42) == 0

    with pytest.raises(Exception):  # FIXME: Not sure what this should be
        assert FormatTransformer(None, type=VariableListType, format="%4s").transform(42) == 0

    with pytest.raises(Exception):  # FIXME: Not sure what this should be
        assert FormatTransformer(None, type=BoundingBoxType, format="%4s").transform((1, -1, -1, 1)) == BoundingBox(
            north=1, west=-1, south=-1, east=1
        )

    b1 = BoundingBox(north=90, west=-45, south=-90, east=45)
    assert FormatTransformer(None, type=BoundingBoxType, format=tuple).transform(b1) == (
        90.0,
        -45.0,
        -90.0,
        45.0,
    )

    assert FormatTransformer(None, type=BoundingBoxType, format="dict").transform(b1) == {
        "east": 45.0,
        "north": 90.0,
        "south": -90.0,
        "west": -45.0,
    }

    assert FormatTransformer(None, type=BoundingBoxType, format=list).transform(b1) == [
        90.0,
        -45.0,
        -90.0,
        45.0,
    ]


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
