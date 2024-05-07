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
import pytest

from climetlab import load_source
from climetlab.testing import MISSING
from climetlab.testing import climetlab_file
from climetlab.utils.dates import to_datetime
from climetlab.utils.dates import to_datetime_list


def test_to_datetime_1():
    pydate = datetime.datetime(2016, 1, 1)

    assert to_datetime(np.datetime64("2016-01-01")) == pydate

    assert to_datetime(np.datetime64("2016-01-01 00:00:00")) == pydate

    assert to_datetime(datetime.date(2016, 1, 1)) == pydate

    assert to_datetime("2016-01-01") == pydate

    assert to_datetime("2016-01-01T00:00:00") == pydate


def test_to_datetime_2():
    assert to_datetime("1851-06-25T00:00") == datetime.datetime(1851, 6, 25)
    assert to_datetime("1851-06-25T06:00") == datetime.datetime(1851, 6, 25, 6)
    assert to_datetime("1851-06-25") == datetime.datetime(1851, 6, 25)

    assert to_datetime("18510625") == datetime.datetime(1851, 6, 25)
    assert to_datetime(18510625) == datetime.datetime(1851, 6, 25)

    assert to_datetime("1851-06-25 06:00:00") == datetime.datetime(1851, 6, 25, 6)
    assert to_datetime("1851-06-25T06:00:00") == datetime.datetime(1851, 6, 25, 6)
    assert to_datetime("1851-06-25T06:00:00Z") == datetime.datetime(1851, 6, 25, 6, tzinfo=datetime.timezone.utc)

    assert to_datetime(-2) == to_datetime(0) - datetime.timedelta(days=2)


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
    assert to_datetime_list("2000-01-01/to/2000-01-05") == [
        datetime.datetime(2000, 1, 1),
        datetime.datetime(2000, 1, 2),
        datetime.datetime(2000, 1, 3),
        datetime.datetime(2000, 1, 4),
        datetime.datetime(2000, 1, 5),
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

    assert to_datetime_list(datetime.datetime(2000, 1, 7)) == [datetime.datetime(2000, 1, 7)]
    assert to_datetime_list([datetime.datetime(2000, 1, 7)]) == [datetime.datetime(2000, 1, 7)]
    assert to_datetime_list(
        [
            datetime.datetime(2000, 1, 4),
            datetime.datetime(2000, 1, 7),
        ]
    ) == [
        datetime.datetime(2000, 1, 4),
        datetime.datetime(2000, 1, 7),
    ]


def test_to_datetimes_list_grib():
    source = load_source("file", climetlab_file("docs/examples/test.grib"))
    for s in source:
        assert to_datetime_list(s) == [datetime.datetime(2020, 5, 13, 12, 0)]


def test_pandas_dates():
    import pandas as pd

    assert to_datetime_list(pd.date_range(start="2020-01-02", end="2020-01-16", freq="w-thu")) == [
        datetime.datetime(2020, 1, 2),
        datetime.datetime(2020, 1, 9),
        datetime.datetime(2020, 1, 16),
    ]


def test_pandas_dates_2():
    import pandas as pd

    d = pd.Series(
        [
            pd.Timestamp(datetime.datetime(2020, 1, 2, 0, 0)),
            pd.Timestamp(datetime.datetime(2020, 1, 9, 0, 0)),
        ]
    )

    assert to_datetime_list(d) == [
        datetime.datetime(2020, 1, 2),
        datetime.datetime(2020, 1, 9),
    ]


@pytest.mark.skipif(MISSING("zarr", "s3fs"), reason="zarr or s3fs not installed")
def test_zarr_dates():
    S3_URL = "https://object-store.os-api.cci1.ecmwf.int/climetlab/test-data/0.5/fixtures"
    source = load_source(
        "zarr-s3",
        [
            f"{S3_URL}/zarr/mini-rt-20200109.zarr",
            f"{S3_URL}/zarr/mini-rt-20200102.zarr",
        ],
    )

    print(to_datetime_list(source.to_xarray().forecast_time))

    assert to_datetime_list(source.to_xarray().forecast_time) == [
        datetime.datetime(2020, 1, 2, tzinfo=datetime.timezone.utc),
        datetime.datetime(2020, 1, 9, tzinfo=datetime.timezone.utc),
    ]


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
