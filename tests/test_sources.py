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
import os
import sys

import pytest
from utils import climetlab_file, modules_installed

import climetlab
from climetlab import load_source


def test_file_source_grib():

    s = load_source("file", climetlab_file("docs/examples/test.grib"))
    assert len(s) == 2


def test_file_source_netcdf():
    s = load_source("file", climetlab_file("docs/examples/test.nc"))
    assert len(s) == 2


@pytest.mark.skipif(
    sys.platform == "win32", reason="file:// not working on Windows yet"  # TODO: fix
)
def test_url_file_source():
    filename = os.path.abspath(climetlab_file("docs/examples/test.nc"))
    s = load_source("url", f"file://{filename}")
    assert len(s) == 2


def test_url_ftp_source_anonymous():
    date = datetime.datetime.now() - datetime.timedelta(days=1)
    load_source(
        "url-pattern",
        (
            "ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/"
            "gfs.{date:date(%Y%m%d)}/00/atmos/wafsgfs_P_t00z_intdsk84.grib2"
        ),
        {"date": date},
    )


def test_url_ftp_source_with_user_pass():
    import ftplib

    date = datetime.datetime.now() - datetime.timedelta(days=1)
    try:
        load_source(
            "url-pattern",
            (
                "ftp://wmo:essential@dissemination.ecmwf.int/{date:date(%Y%m%d)}000000/"
                "A_HPXA89ECMF{date:date(%d)}0000_C_ECMF_{date:date(%Y%m%d)}"
                "000000_an_msl_global_0p5deg_grib2.bin"
            ),
            {"date": date},
        )
    except ftplib.error_temp:
        # Sometimes this site returns:
        # ftplib.error_temp: 421 Maximum number of connections exceeded (500)
        pass


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


def test_url_source_1():
    load_source("url", "http://download.ecmwf.int/test-data/metview/gallery/temp.bufr")


def test_url_source_2():
    load_source(
        "url", "https://github.com/ecmwf/climetlab/raw/master/docs/examples/test.grib"
    )


def test_url_source_3():
    load_source(
        "url", "https://github.com/ecmwf/climetlab/raw/master/docs/examples/test.nc"
    )


def test_url_pattern_source_3():
    load_source(
        "url-pattern",
        "https://github.com/ecmwf/climetlab/raw/master/docs/examples/test.{format}",
        {"format": ["nc", "grib"]},
    )
    # source.to_xarray()


S3_URL = "https://storage.ecmwf.europeanweather.cloud/climetlab/test-data/0.5/fixtures"


@pytest.mark.skipif(
    not modules_installed("zarr", "s3fs"), reason="Zarr or S3FS not installed"
)
def test_zarr_source_1():
    source = load_source(
        "zarr-s3",
        f"{S3_URL}/zarr/mini-rt-20200102.zarr",
    )
    ds = source.to_xarray()
    assert len(ds.forecast_time) == 1


@pytest.mark.skipif(
    not modules_installed("zarr", "s3fs"), reason="Zarr or S3FS not installed"
)
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


@pytest.mark.skipif(
    not modules_installed("zarr", "s3fs"), reason="Zarr or S3FS not installed"
)
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


if __name__ == "__main__":
    from utils import main

    main(globals())
