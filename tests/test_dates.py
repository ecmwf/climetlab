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

import numpy as np

from climetlab import load_source
from climetlab.utils.dates import parse_date, to_datetime, to_datetime_list


def test_to_datetime():
    pydate = datetime.datetime(2016, 1, 1)

    assert to_datetime(np.datetime64("2016-01-01")) == pydate

    assert to_datetime(np.datetime64("2016-01-01 00:00:00")) == pydate

    assert to_datetime(datetime.date(2016, 1, 1)) == pydate

    assert to_datetime("2016-01-01") == pydate

    assert to_datetime("2016-01-01T00:00:00") == pydate


def test_parse_date():
    assert parse_date("1851-06-25T00:00") == datetime.datetime(1851, 6, 25)
    assert parse_date("1851-06-25T06:00") == datetime.datetime(1851, 6, 25, 6)
    assert parse_date("1851-06-25") == datetime.datetime(1851, 6, 25)

    assert parse_date("18510625") == datetime.datetime(1851, 6, 25)
    assert parse_date(18510625) == datetime.datetime(1851, 6, 25)

    assert parse_date("1851-06-25 06:00:00") == datetime.datetime(1851, 6, 25, 6)
    assert parse_date("1851-06-25T06:00:00") == datetime.datetime(1851, 6, 25, 6)
    assert parse_date("1851-06-25T06:00:00Z") == datetime.datetime(
        1851, 6, 25, 6, tzinfo=datetime.timezone.utc
    )

    assert parse_date(-2) == parse_date(0) - datetime.timedelta(days=2)


def test_to_datetimes_list():
    assert to_datetime_list("20000101/to/20000103") == [
        datetime.datetime(2000, 1, 1),
        datetime.datetime(2000, 1, 2),
        datetime.datetime(2000, 1, 3),
    ]
    assert to_datetime_list("2000-01-01/to/2000-01-03") == [
        datetime.datetime(2000, 1, 1),
        datetime.datetime(2000, 1, 2),
        datetime.datetime(2000, 1, 3),
    ]
    assert to_datetime_list("2000-01-01/to/2000-01-10/by/3") == [
        datetime.datetime(2000, 1, 1),
        datetime.datetime(2000, 1, 4),
        datetime.datetime(2000, 1, 7),
        datetime.datetime(2000, 1, 10),
    ]
    assert to_datetime_list((20000101, "to", 20000103)) == [
        datetime.datetime(2000, 1, 1),
        datetime.datetime(2000, 1, 2),
        datetime.datetime(2000, 1, 3),
    ]

    assert to_datetime_list(("2000-01-01", "to", "2000-01-10", "by", "3")) == [
        datetime.datetime(2000, 1, 1),
        datetime.datetime(2000, 1, 4),
        datetime.datetime(2000, 1, 7),
        datetime.datetime(2000, 1, 10),
    ]

    assert len(to_datetime_list((-10, "to", -1))) == 10


def test_to_datetimes_list_grib():
    source = load_source("file", "docs/examples/test.grib")
    for s in source:
        assert to_datetime_list(s) == [datetime.datetime(2020, 5, 13, 12, 0)]


def test_pandas_dates():
    import pandas as pd

    assert to_datetime_list(
        pd.date_range(start="2020-01-02", end="2020-01-16", freq="w-thu")
    ) == [
        datetime.datetime(2020, 1, 2),
        datetime.datetime(2020, 1, 9),
        datetime.datetime(2020, 1, 16),
    ]


if __name__ == "__main__":
    # test_to_datetime()
    test_pandas_dates()
