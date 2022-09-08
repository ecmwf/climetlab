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

import climetlab as cml
from climetlab.testing import climetlab_file


def grib_filename():
    return climetlab_file("docs/examples/test4.grib")


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
def _test_file_source_order_with_request(params, levels):
    ds = cml.load_source(
        "file",
        grib_filename(),
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
def _test_file_source_order_with_order_by_method_1(params, levels):
    ds = cml.load_source(
        "file",
        grib_filename(),
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


def _test_file_source_order_with_order_by_method_2():
    params = ["z", "t"]
    levels = [500, 850]
    ds = cml.load_source("file", grib_filename())
    ds = ds.sel(
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


def _test_file_source_sel_in_load_source():
    params = ["z", "t"]
    levels = [500]
    ds = cml.load_source(
        "file",
        grib_filename(),
        variable=params,
        level=levels,
    )
    assert len(ds) == 2


def _test_file_source_sel():
    params = ["z", "t"]
    levels = [500, 850]
    ds = cml.load_source("file", grib_filename())
    ds = ds.sel(
        variable=params,
        level=levels,
    )
    assert len(ds) == 2


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
def _test_file_source_order_with_order_by_keyword(params, levels):

    ds = cml.load_source(
        "file",
        grib_filename(),
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


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
    # test_directory_source_with_none_2(
    # test_directory_source_with_none_1(
    # _test_file_source_order_with_order_by_method_2()
    # test_directory_source_order_with_order_by_method_1(
    #    ["z", "t"],
    #    [500, 850],
    # )
