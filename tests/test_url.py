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
import pathlib
import time

import climetlab as cml
from climetlab import settings
from climetlab.testing import data_file_url
from climetlab.utils import download_and_cache


def path_to_url(path):
    return pathlib.Path(os.path.abspath(path)).as_uri()


def test_download_1():
    url = (
        "https://github.com/ecmwf/climetlab/raw/master/docs/examples/test.grib?_=%s"
        % (time.time(),)
    )
    download_and_cache(url)


def test_download_2():
    url = "https://github.com/ecmwf/climetlab/raw/master/docs/examples/test.grib"
    download_and_cache(url)


def test_download_3():
    with settings.temporary("download-updated-urls", True):
        url = "https://datastore.copernicus-climate.eu/climetlab/test.txt"
        download_and_cache(url)


# def test_local():
#     ds = cml.load_source(
#         "url",
#         data_file_url("single", "z_500_20000101.grib"),
#     )
#     assert len(ds) == 1


def test_ftp():
    pass


# TODO: test .tar, .zip, .tar.gz

if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
