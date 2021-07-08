#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging
import os

from climetlab import load_source
from climetlab.core.temporary import temp_directory, temp_file
from climetlab.testing import data_file_url

LOG = logging.getLogger(__name__)


def test_multi_directory_1():
    with temp_directory() as directory:
        for date in (20000101, 20000102):
            ds = load_source("dummy-source", kind="grib", date=date)
            ds.save(os.path.join(directory, f"{date}.grib"))

        ds = load_source("file", directory)
        print(ds)
        assert len(ds) == 2

        with temp_file() as filename:
            ds.save(filename)
            ds = load_source("file", filename)
            assert len(ds) == 2


# def test_multi_directory_2():
#     ds = load_source(
#         "url",
#         data_file_url("mixed"),
#     )
#     print(ds)
#     # assert len(ds) == 1


# def test_grib_zip():
#     # ds =
#     load_source(
#         "url",
#         data_file_url("grib.zip"),
#     )
#     # assert len(ds) == 1


def test_multi_grib():
    ds = load_source(
        "multi",
        load_source("dummy-source", kind="grib", date=20000101),
        load_source("dummy-source", kind="grib", date=20000102),
    )
    assert len(ds) == 2


def test_multi_grib_mixed():
    ds = load_source(
        "multi",
        load_source("dummy-source", kind="grib", date=20000101),
        load_source("dummy-source", kind="grib", date=20000102),
        load_source("dummy-source", kind="unknown", hello="world"),
    )
    assert len(ds) == 2


# def test_download_tar():
#     ds = load_source(
#         "url",
#         "https://datastore.copernicus-climate.eu/climetlab/grib.tar",
#     )
#     assert len(ds) == 2, len(ds)


# def test_download_tgz():
#     ds = load_source(
#         "url",
#         "https://datastore.copernicus-climate.eu/climetlab/grib.tgz",
#     )
#     assert len(ds) == 2, len(ds)

# def test_download_tar_gz():
#     ds = load_source(
#         "url",
#         "https://datastore.copernicus-climate.eu/climetlab/grib.tar.gz",
#     )
#     assert len(ds) == 2, len(ds)

# def test_download_gz():
#     ds = load_source(
#         "url",
#         "https://datastore.copernicus-climate.eu/climetlab/grib.gz",
#     )
#     assert len(ds) == 2, len(ds)

if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
