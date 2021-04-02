#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import sys

import pytest

from climetlab import load_source, source


def test_file_source_grib():
    s = load_source("file", "docs/examples/test.grib")
    assert len(s) == 2


def test_file_source_netcdf():
    s = load_source("file", "docs/examples/test.nc")
    assert len(s) == 2


@pytest.mark.skipif(
    True or sys.version_info < (3, 7), reason="Version 3.7 or greater needed"
)
def test_file_source_shortcut():
    s = source.file("docs/examples/test.grib")
    assert len(s) == 2


def test_file_source_mars():

    if not os.path.exists(os.path.expanduser("~/.ecmwfapirc")):
        pytest.skip("No ~/.ecmwfapirc")

    s = load_source(
        "mars",
        param=["2t", "msl"],
        levtype="sfc",
        area=[50, -50, 20, 50],
        grid=[1, 1],
        date="2012-12-13",
    )
    assert len(s) == 2


def test_file_source_cds_grib():

    if not os.path.exists(os.path.expanduser("~/.cdsapirc")):
        pytest.skip("No ~/.cdsapirc")

    s = load_source(
        "cds",
        "reanalysis-era5-single-levels",
        variable=["2t", "msl"],
        product_type="reanalysis",
        area=[50, -50, 20, 50],
        date="2012-12-12",
        time="12:00",
    )
    assert len(s) == 2


def test_file_source_cds_netcdf():

    if not os.path.exists(os.path.expanduser("~/.cdsapirc")):
        pytest.skip("No ~/.cdsapirc")

    s = load_source(
        "cds",
        "reanalysis-era5-single-levels",
        variable=["2t", "msl"],
        product_type="reanalysis",
        area=[50, -50, 20, 50],
        date="2012-12-12",
        time="12:00",
        format="netcdf",
    )
    assert len(s) == 2


def test_ulr_source_1():
    load_source("url", "http://download.ecmwf.int/test-data/metview/gallery/temp.bufr")


def test_ulr_source_2():
    load_source(
        "url", "https://github.com/ecmwf/climetlab/raw/master/docs/examples/test.grib"
    )


def test_ulr_source_3():
    load_source(
        "url", "https://github.com/ecmwf/climetlab/raw/master/docs/examples/test.nc"
    )


def zarr_not_installed():
    try:
        import s3fs  # noqa
        import zarr  # noqa

        return False
    except ImportError:
        return True


S3_URL = "https://storage.ecmwf.europeanweather.cloud/s2s-ai-competition/data/fixtures"


@pytest.mark.skipif(zarr_not_installed(), reason="Zarr or S3FS not installed")
def test_zarr_source_1():
    source = load_source(
        "zarr-s3",
        f"{S3_URL}/0.1.20/zarr/mini-rt-20200102.zarr",
    )
    ds = source.to_xarray()
    assert len(ds.forecast_time) == 1


@pytest.mark.skipif(zarr_not_installed(), reason="Zarr or S3FS not installed")
def test_zarr_source_2():
    import datetime

    from climetlab.utils.dates import to_datetime_list

    source = load_source(
        "zarr-s3",
        [
            f"{S3_URL}/0.1.20/zarr/mini-rt-20200109.zarr",
            f"{S3_URL}/0.1.20/zarr/mini-rt-20200102.zarr",
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


@pytest.mark.skipif(zarr_not_installed(), reason="Zarr or S3FS not installed")
def test_zarr_source_3():
    import datetime

    from climetlab.utils.dates import to_datetime_list

    source = load_source(
        "zarr-s3",
        [
            f"{S3_URL}/0.1.20/zarr/mini-hc-20200109.zarr",
            f"{S3_URL}/0.1.20/zarr/mini-hc-20200102.zarr",
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


if __name__ == "__main__":
    test_file_source_cds_netcdf()
