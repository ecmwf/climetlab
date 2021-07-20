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

import pytest

from climetlab import load_source
from climetlab.core.temporary import temp_directory, temp_file

LOG = logging.getLogger(__name__)


def test_multi_graph_1():
    a11 = load_source("dummy-source", kind="grib", date=20000101)
    a12 = load_source("dummy-source", kind="grib", date=20000102)
    b11 = load_source("dummy-source", kind="grib", date=20000103)
    b12 = load_source("dummy-source", kind="grib", date=20000104)

    a21 = load_source("dummy-source", kind="grib", date=20000105)
    a22 = load_source("dummy-source", kind="grib", date=20000106)
    b21 = load_source("dummy-source", kind="grib", date=20000107)
    b22 = load_source("dummy-source", kind="grib", date=20000108)

    m1 = load_source(
        "multi",
        load_source("multi", a11, a12),
        load_source("multi", b11, b12),
    )

    m2 = load_source(
        "multi",
        load_source("multi", a21, a22),
        load_source("multi", b21, b22),
    )

    ds = load_source("multi", m1, m2)
    ds.graph()

    assert len(ds) == 8
    ds.to_xarray()


def test_multi_graph_2():
    with temp_directory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, "a1"))
        a11 = load_source("dummy-source", kind="grib", date=20000101)
        a11.save(os.path.join(tmpdir, "a1", "a11.grib"))
        a12 = load_source("dummy-source", kind="grib", date=20000102)
        a12.save(os.path.join(tmpdir, "a1", "a12.grib"))

        os.mkdir(os.path.join(tmpdir, "b1"))
        b11 = load_source("dummy-source", kind="grib", date=20000103)
        b11.save(os.path.join(tmpdir, "b1", "b11.grib"))
        b12 = load_source("dummy-source", kind="grib", date=20000104)
        b12.save(os.path.join(tmpdir, "b1", "b12.grib"))

        os.mkdir(os.path.join(tmpdir, "a2"))
        a21 = load_source("dummy-source", kind="grib", date=20000105)
        a21.save(os.path.join(tmpdir, "a2", "a21.grib"))
        a22 = load_source("dummy-source", kind="grib", date=20000106)
        a22.save(os.path.join(tmpdir, "a2", "a22.grib"))

        os.mkdir(os.path.join(tmpdir, "b2"))
        b21 = load_source("dummy-source", kind="grib", date=20000107)
        b21.save(os.path.join(tmpdir, "b2", "b21.grib"))
        b22 = load_source("dummy-source", kind="grib", date=20000108)
        b22.save(os.path.join(tmpdir, "b2", "b22.grib"))

        def filter(path_or_url):
            return path_or_url.endswith("2.grib")

        ds = load_source("file", tmpdir, filter=filter)
        ds.graph()

        assert len(ds) == 4


def test_multi_directory_1():
    with temp_directory() as directory:
        for date in (20000101, 20000102):
            ds = load_source("dummy-source", kind="grib", date=date)
            ds.save(os.path.join(directory, f"{date}.grib"))

        ds = load_source("file", directory)
        print(ds)
        assert len(ds) == 2
        ds.graph()

        with temp_file() as filename:
            ds.save(filename)
            ds = load_source("file", filename)
            assert len(ds) == 2


@pytest.mark.skipif(True, reason="Test not yet implemented")
def test_download_zip_2():
    def filter(path_or_url):
        LOG.debug("test_download_zip_2.filter %s", path_or_url)
        if path_or_url.startswith("http") and path_or_url.endswith("d.zip"):
            return False
        return True

    ds = load_source(
        "url-pattern",
        "https://get.ecmwf.int/repository/test-data/climetlab/grib-{x}.zip",
        x=["c", "d"],
        filter=filter,
    )

    ds.graph()
    assert len(ds) == 18, len(ds)


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


def xtest_multi_grib():
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


def test_download_tar():
    ds = load_source(
        "url",
        "https://get.ecmwf.int/repository/test-data/climetlab/grib.tar",
    )
    assert len(ds) == 6, len(ds)


def test_download_tgz():
    ds = load_source(
        "url",
        "https://get.ecmwf.int/repository/test-data/climetlab/grib.tgz",
    )
    assert len(ds) == 6, len(ds)


def test_download_tar_gz():
    ds = load_source(
        "url",
        "https://get.ecmwf.int/repository/test-data/climetlab/grib.tar.gz",
    )
    assert len(ds) == 6, len(ds)


@pytest.mark.skipif(True, reason="Not yet implemented")
def test_download_gz():
    ds = load_source(
        "url",
        "https://get.ecmwf.int/repository/test-data/climetlab/grib.gz",
    )
    assert len(ds) == 2, len(ds)


def test_download_zip_1():
    ds = load_source(
        "url",
        "https://get.ecmwf.int/repository/test-data/climetlab/grib.zip",
    )

    assert len(ds) == 6, len(ds)


def test_download_zip_3():
    ds = load_source(
        "url-pattern",
        "https://get.ecmwf.int/repository/test-data/climetlab/grib-{param}.zip",
        param=["2t", "msl"],
    )

    ds.graph()
    assert len(ds) == 6, len(ds)


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
