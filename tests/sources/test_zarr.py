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

NOT_S3_URL = "https://get.ecmwf.int/test-data/climetlab/fixtures"
S3_URL = "https://storage.ecmwf.europeanweather.cloud/climetlab/test-data/0.5/fixtures"
S3_URL2 = "s3://storage.ecmwf.europeanweather.cloud/climetlab/test-data/0.5/fixtures"


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
    assert dates[0] == datetime.datetime(2020, 1, 2)
    assert dates[1] == datetime.datetime(2020, 1, 9)

    dates = to_datetime_list(ds.forecast_time.values)
    assert dates[0] == datetime.datetime(2020, 1, 2)
    assert dates[1] == datetime.datetime(2020, 1, 9)


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
    assert dates[0] == datetime.datetime(2000, 1, 2)
    assert dates[1] == datetime.datetime(2000, 1, 9)
    assert dates[2] == datetime.datetime(2001, 1, 2)
    assert dates[3] == datetime.datetime(2001, 1, 9)

    dates = to_datetime_list(ds.forecast_time.values)
    assert dates[0] == datetime.datetime(2000, 1, 2)
    assert dates[1] == datetime.datetime(2000, 1, 9)
    assert dates[2] == datetime.datetime(2001, 1, 2)
    assert dates[3] == datetime.datetime(2001, 1, 9)


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
        "dummy-source",
        kind="zarr",
    )
    ds = s.to_xarray()
    assert "lat" in ds.dims


@pytest.mark.skipif(MISSING("zarr"), reason="Zarr not installed")
def test_zarr_from_zip_file():
    s = load_source(
        "dummy-source",
        kind="zarr-zip",
    )
    ds = s.to_xarray()
    assert "lat" in ds.dims


@pytest.mark.skipif(MISSING("zarr", "s3fs"), reason="Zarr or S3FS not installed")
def test_https_does_not_support_zarr():
    # If the http(s) server is not a s3 server,
    # it does not work
    with pytest.raises(Exception):
        source = load_source(
            "zarr-s3",
            f"{NOT_S3_URL}/zarr/mini-rt-20200102.zarr",
        )
        ds = source.to_xarray()
        assert len(ds.forecast_time) == 1


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
