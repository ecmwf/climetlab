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
import sys

import numpy as np
import pytest

from climetlab import load_source
from climetlab.decorators import normalize
from climetlab.testing import climetlab_file


def test_normalize_dates_from_source():
    @normalize("date", "date")
    def dates_3(date):
        return date

    @normalize("date", "date", multiple=True)
    def dates_list_3(date):
        return date

    source = load_source("file", climetlab_file("docs/examples/test.grib"))
    assert dates_3(source[0]) == datetime.datetime(2020, 5, 13, 12, 0)
    assert dates_list_3(source[0]) == [datetime.datetime(2020, 5, 13, 12, 0)]

    source = load_source("file", climetlab_file("docs/examples/test.nc"))

    #  For now
    with pytest.raises(NotImplementedError):
        assert dates_3(source[0]) == datetime.datetime(2020, 5, 13, 12, 0)
        assert dates_list_3(source[0]) == [datetime.datetime(2020, 5, 13, 12, 0)]


def test_dates_no_list():
    norm = DateNormaliser("%Y.%m.%d")
    assert norm("20200513") == ["2020.05.13"]
    assert norm([datetime.datetime(2020, 5, 13, 0, 0)]) == ["2020.05.13"]
    assert norm([datetime.datetime(2020, 5, 13, 23, 59)]) == ["2020.05.13"]


# def test_dates_with_list():
#     norm = DateNormaliser("%Y.%m.%d", valid=["2020.05.13"] )
#     assert norm("20200513") == ["2020.05.13"]
#     assert norm([datetime.datetime(2020, 5, 13, 12, 0)]) == ["2020.05.13"]
#
#     with pytest.raises(ValueError):
#         assert norm("19991231")


def test_dates_3():
    norm = DateNormaliser()
    assert norm("20200513") == [datetime.datetime(2020, 5, 13, 0, 0)]
    assert norm([datetime.datetime(2020, 5, 13, 0, 0)]) == [
        datetime.datetime(2020, 5, 13, 0, 0)
    ]


if __name__ == "__main__":

    from climetlab.testing import main

    main(__file__)
