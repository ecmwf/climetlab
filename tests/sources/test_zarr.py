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

from climetlab import load_source
from climetlab.testing import MISSING
from climetlab.testing import TEST_DATA_URL

NOT_S3_URL = f"{TEST_DATA_URL}/input"
S3_URL = "https://object-store.os-api.cci1.ecmwf.int/climetlab/test-data/0.5/fixtures"
S3_URL2 = "s3://object-store.os-api.cci1.ecmwf.int/climetlab/test-data/0.5/fixtures"


@pytest.mark.skipif(MISSING("zarr", "s3fs"), reason="Zarr or S3FS not installed")
def test_zarr_source_1():
    source = load_source(
        "zarr-s3",
        f"{S3_URL}/zarr/mini-rt-20200102.zarr",
    )
    ds = source.to_xarray()
    assert len(ds.forecast_time) == 1


@pytest.mark.skipif(MISSING("zarr", "s3fs"), reason="Zarr or S3FS not installed")
def test_zarr_source_2():
    import datetime

    from climetlab.utils.dates import to_datetime_list

    source = load_source(
        "zarr-s3",
        [
            f"{S3_URL}/zarr/mini-rt-20200109.zarr",
            f"{S3_URL}/zarr/mini-rt-20200102.zarr",
        ],
    )

    ds = source.to_xarray()
    assert len(ds.forecast_time) == 2

    dates = to_datetime_list(ds.forecast_time)
    assert dates[0].strftime("%Y-%m-%d") == datetime.datetime(2020, 1, 2).strftime("%Y-%m-%d")
    assert dates[1].strftime("%Y-%m-%d") == datetime.datetime(2020, 1, 9).strftime("%Y-%m-%d")

    dates = to_datetime_list(ds.forecast_time.values)
    assert dates[0].strftime("%Y-%m-%d") == datetime.datetime(2020, 1, 2).strftime("%Y-%m-%d")
    assert dates[1].strftime("%Y-%m-%d") == datetime.datetime(2020, 1, 9).strftime("%Y-%m-%d")


@pytest.mark.skipif(MISSING("zarr", "s3fs"), reason="Zarr or S3FS not installed")
def test_zarr_source_3():
    import datetime

    from climetlab.utils.dates import to_datetime_list

    source = load_source(
        "zarr-s3",
        [
            f"{S3_URL}/zarr/mini-hc-20200109.zarr",
            f"{S3_URL}/zarr/mini-hc-20200102.zarr",
        ],
    )
    ds = source.to_xarray()
    assert len(ds.forecast_time) == 8

    dates = to_datetime_list(ds.forecast_time)
    assert dates[0].strftime("%Y-%m-%d") == datetime.datetime(2000, 1, 2).strftime("%Y-%m-%d")
    assert dates[1].strftime("%Y-%m-%d") == datetime.datetime(2000, 1, 9).strftime("%Y-%m-%d")
    assert dates[2].strftime("%Y-%m-%d") == datetime.datetime(2001, 1, 2).strftime("%Y-%m-%d")
    assert dates[3].strftime("%Y-%m-%d") == datetime.datetime(2001, 1, 9).strftime("%Y-%m-%d")

    dates = to_datetime_list(ds.forecast_time.values)
    assert dates[0].strftime("%Y-%m-%d") == datetime.datetime(2000, 1, 2).strftime("%Y-%m-%d")
    assert dates[1].strftime("%Y-%m-%d") == datetime.datetime(2000, 1, 9).strftime("%Y-%m-%d")
    assert dates[2].strftime("%Y-%m-%d") == datetime.datetime(2001, 1, 2).strftime("%Y-%m-%d")
    assert dates[3].strftime("%Y-%m-%d") == datetime.datetime(2001, 1, 9).strftime("%Y-%m-%d")


@pytest.mark.skipif(MISSING("zarr", "s3fs"), reason="Zarr or S3FS not installed")
def test_zarr_source_4():
    source = load_source("zarr", f"{S3_URL}/zarr/mini-rt-20200102.zarr")
    ds = source.to_xarray()
    assert len(ds.forecast_time) == 1


@pytest.mark.skipif(MISSING("zarr", "s3fs"), reason="Zarr or S3FS not installed")
def test_zarr_source_5():
    source = load_source("zarr", f"{S3_URL2}/zarr/mini-rt-20200102.zarr")
    ds = source.to_xarray()
    assert len(ds.forecast_time) == 1


@pytest.mark.skipif(MISSING("zarr"), reason="Zarr not installed")
def test_zarr_from_directory():
    s = load_source(
        "climetlab-testing",
        kind="zarr",
    )
    ds = s.to_xarray()
    assert "lat" in ds.dims


@pytest.mark.skipif(MISSING("zarr"), reason="Zarr not installed")
def test_zarr_from_zip_file():
    s = load_source(
        "climetlab-testing",
        kind="zarr-zip",
    )
    ds = s.to_xarray()
    assert "lat" in ds.dims


# @pytest.skip(reason="The test http server does not allow zarr hosting from outside of ECMWF.")
@pytest.mark.skipif(MISSING("zarr", "s3fs"), reason="Zarr or S3FS not installed")
def test_http_does_support_zarr():
    source = load_source(
        "zarr-s3",
        f"{NOT_S3_URL}/mini-rt-20200102.zarr",
    )
    ds = source.to_xarray()
    assert len(ds.forecast_time) == 1


if __name__ == "__main__":
    from climetlab.testing import main

    # test_http_does_not_support_zarr()
    main(__file__)
