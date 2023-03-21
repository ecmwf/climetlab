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
import shutil
from contextlib import contextmanager

from climetlab.utils import download_and_cache

TEST_DATA_URL = (
    "https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/grib"
)
TEST_DATA_URL_ALT = (
    "https://storage.ecmwf.europeanweather.cloud/climetlab/test-data/input/grib"
)
# CML_BASEURL_CDS = "https://datastore.copernicus-climate.eu/climetlab"


def build_testdata(dir="testdata"):
    os.makedirs(dir, exist_ok=True)
    for path in [
        "2t-tp.grib",
        "all.grib",
        "all/climetlab.json",
        "all/u.grib",
        "all/v.grib",
        "all/z.grib",
        "all/2t.grib",
        "all/climetlab.json",
        "all/tp.grib",
        "all/lsm.grib",
        "climetlab.json",
        "lsm.grib",
        "pl/climetlab.json",
        "pl/u.grib",
        "pl/v.grib",
        "pl/z.grib",
        "sfc/2t.grib",
        "sfc/climetlab.json",
        "sfc/tp.grib",
        "uvz.grib",
    ]:
        outpath = os.path.join(dir, path)
        if os.path.exists(outpath):
            continue
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        shutil.copyfile(download_and_cache(TEST_DATA_URL + "/" + path), outpath)

    return dir


@contextmanager
def cd(dir):
    old = os.getcwd()
    os.chdir(os.path.expanduser(dir))
    try:
        yield dir
    finally:
        os.chdir(old)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
