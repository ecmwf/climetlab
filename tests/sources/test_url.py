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
import mimetypes
import os
import sys

import pytest

from climetlab import load_source
from climetlab.sources.url import canonical_extension
from climetlab.testing import TEST_DATA_URL, climetlab_file


@pytest.mark.skipif(  # TODO: fix
    sys.platform == "win32",
    reason="file:// not working on Windows yet",
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


def test_url_source_1():
    load_source(
        "url",
        "http://download.ecmwf.int/test-data/metview/gallery/temp.bufr",
    )


def test_url_source_2():
    load_source(
        "url",
        "https://github.com/ecmwf/climetlab/raw/main/docs/examples/test.grib",
    )


def test_url_source_3():
    load_source(
        "url",
        "https://github.com/ecmwf/climetlab/raw/main/docs/examples/test.nc",
    )


def test_mimetypes():
    assert mimetypes.guess_type("x.grib") == ("application/x-grib", None)
    assert canonical_extension("x.grib") == ".grib"
    assert canonical_extension("x.grib1") == ".grib"
    assert canonical_extension("x.grib2") == ".grib"

    assert mimetypes.guess_type("x.nc") == ("application/x-netcdf", None)
    assert canonical_extension("x.nc") == ".nc"
    assert canonical_extension("x.nc4") == ".nc"
    assert canonical_extension("x.cdf") == ".nc"
    assert canonical_extension("x.netcdf") == ".nc"


def test_canonical_extension():
    assert canonical_extension("x.tar") == ".tar"
    assert canonical_extension("x.tgz") == ".tar.gz"
    assert canonical_extension("x.foo") == ".foo"
    assert canonical_extension("x.csv") == ".csv"
    assert canonical_extension("x.csv.gz") == ".csv.gz"


def test_extension():

    s = load_source(
        "url",
        f"{TEST_DATA_URL}/fixtures/tfrecord/EWCTest0.0.tfrecord",
    )
    assert s.path.endswith(".0.tfrecord")
    s = load_source(
        "url",
        f"{TEST_DATA_URL}/fixtures/tfrecord/EWCTest0.1.tfrecord",
    )
    assert s.path.endswith(".1.tfrecord")


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
