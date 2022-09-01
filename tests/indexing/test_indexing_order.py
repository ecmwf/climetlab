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

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_indexing_order.py.grib")


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
def _test_order_directory_source_1(params, levels):
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
    assert ds[0].handle.get("shortName") == params[0]
    assert ds[1].handle.get("shortName") == params[0]
    assert ds[2].handle.get("shortName") == params[1]
    assert ds[3].handle.get("shortName") == params[1]
    print()


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
def test_order_directory_source_2(params, levels):
    ds = cml.load_source(
        "directory",
        TEST_DIR,
        level=levels,
        variable=params,
        date=20070101,
        time="1200",
    )
    for i in ds:
        print(i)
    assert len(ds) == 4
    assert ds[0].handle.get("shortName") == params[0]
    assert ds[1].handle.get("shortName") == params[1]
    assert ds[2].handle.get("shortName") == params[0]
    assert ds[3].handle.get("shortName") == params[1]
    print()


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
def _test_order_directory_source_with_none_1(params):
    ds = cml.load_source(
        "directory",
        TEST_DIR,
        variable=params,
        level=None,
        date=20070101,
        time="1200",
    )
    for i in ds:
        print(i)
    assert len(ds) == 4
    assert ds[0].handle.get("shortName") == params[0]
    assert ds[1].handle.get("shortName") == params[1]
    assert ds[2].handle.get("shortName") == params[0]
    assert ds[3].handle.get("shortName") == params[1]
    print()


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
def _test_order_directory_source_with_none_2(params):
    ds = cml.load_source(
        "directory",
        TEST_DIR,
        level=None,
        variable=params,
        date=20070101,
        time="1200",
    )
    print(params)
    print(len(ds))
    for i in ds:
        print(i)
    assert ds[0].handle.get("shortName") == params[0]
    assert ds[1].handle.get("shortName") == params[1]
    assert ds[2].handle.get("shortName") == params[0]
    assert ds[3].handle.get("shortName") == params[1]
    print()


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
