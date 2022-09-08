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

import pytest

import climetlab as cml
from climetlab.core.temporary import temp_directory
from climetlab.testing import climetlab_file


@pytest.fixture
def dir_with_grib_files():
    tmp = temp_directory()
    testdir = tmp.path
    _build_dir_with_grib_files(testdir)
    yield tmp.path


def _build_dir_with_grib_files(testdir):
    import shutil

    os.makedirs(testdir, exist_ok=True)
    for p in ["docs/examples/test.grib", "docs/examples/test4.grib"]:
        path = climetlab_file(p)
        shutil.copy(path, testdir)


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
def _test_directory_source_1(params, levels):
    home = os.path.expanduser("~")
    ds = cml.load_source(
        "directory",
        f"{home}/links/weather-bench-links/data-from-mc-symlinks-to-files",
        variable=params,
        level=levels,
        date=20070101,
        time="1200",
    )
    print(params)
    print(len(ds))
    for i in ds:
        print(i)
    assert ds[0].metadata("short_name") == params[0]
    assert ds[1].metadata("short_name") == params[1]
    assert ds[2].metadata("short_name") == params[0]
    assert ds[3].metadata("short_name") == params[1]
    print()


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
def test_directory_source_order_with_request(params, levels, dir_with_grib_files):
    ds = cml.load_source(
        "directory",
        dir_with_grib_files,
        level=levels,
        variable=params,
        date=20070101,
        time="1200",
    )
    for i in ds:
        print(i)
    assert len(ds) == 4
    assert ds[0].metadata("short_name") == params[0]
    assert ds[1].metadata("short_name") == params[1]
    assert ds[2].metadata("short_name") == params[0]
    assert ds[3].metadata("short_name") == params[1]
    print()


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
def test_directory_source_order_with_order_by_method_1(
    params, levels, dir_with_grib_files
):
    ds = cml.load_source(
        "directory",
        dir_with_grib_files,
        variable=["t", "z"],
        level=[500, 850],
    ).order_by(
        level=[str(x) for x in levels],
        variable=params,
        date=None,
        time=None,
    )
    for i in ds:
        print(i)
    assert len(ds) == 4
    assert ds[0].metadata("short_name") == params[0]
    assert ds[1].metadata("short_name") == params[1]
    assert ds[2].metadata("short_name") == params[0]
    assert ds[3].metadata("short_name") == params[1]

    assert ds[0].metadata("level") == levels[0]
    assert ds[1].metadata("level") == levels[0]
    assert ds[2].metadata("level") == levels[1]
    assert ds[3].metadata("level") == levels[1]


def test_directory_source_order_with_order_by_method_2(dir_with_grib_files):
    params = ["z", "t"]
    levels = [500, 850]
    ds = cml.load_source(
        "directory",
        dir_with_grib_files,
        variable=params,
        level=levels,
    )
    ds = ds.order_by(
        level="ascending",
        variable="descending",
    )
    for i in ds:
        print(i)
    assert len(ds) == 4
    assert ds[0].metadata("short_name") == params[0]
    assert ds[1].metadata("short_name") == params[1]
    assert ds[2].metadata("short_name") == params[0]
    assert ds[3].metadata("short_name") == params[1]


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
def test_directory_source_order_with_order_by_keyword(
    params, levels, dir_with_grib_files
):

    ds = cml.load_source(
        "directory",
        dir_with_grib_files,
        variable=params,
        level=levels,
        order_by=dict(
            level=None,
            variable=params,
            # date=20070101,
        ),
    )
    for i in ds:
        print(i)
    assert len(ds) == 4
    assert ds[0].metadata("short_name") == params[0]
    assert ds[1].metadata("short_name") == params[1]
    assert ds[2].metadata("short_name") == params[0]
    assert ds[3].metadata("short_name") == params[1]


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
def test_directory_source_with_none_1(params, dir_with_grib_files):
    ds = cml.load_source(
        "directory",
        dir_with_grib_files,
        level=None,
        variable=params,
        date=20070101,
        time="1200",
    )
    for i in ds:
        print(i)
    assert len(ds) == 4
    assert ds[0].metadata("short_name") == params[0]
    assert ds[1].metadata("short_name") == params[1]
    assert ds[2].metadata("short_name") == params[0]
    assert ds[3].metadata("short_name") == params[1]


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)

    # testdir = "test_indexing_tmpdir"
    # _build_dir_with_grib_files(testdir)

    # test_directory_source_order_with_order_by_method_2(testdir)
    # test_directory_source_order_with_order_by_method_1(
    #    ["z", "t"],
    #    [500, 850],
    # )
