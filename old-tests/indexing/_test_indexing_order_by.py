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

here = os.path.dirname(__file__)
sys.path.insert(0, here)
from indexing_fixtures import check_sel_and_order  # noqa: E402
from indexing_fixtures import get_fixtures


@pytest.mark.parametrize("params", (["t", "u"], ["u", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
# @pytest.mark.parametrize("source_name", ["indexed-directory", "list-of-dicts", "file"])
@pytest.mark.parametrize("source_name", ["indexed-directory"])
def test_indexing_order_by_with_request(params, levels, source_name):
    request = dict(
        level=levels,
        variable=params,
        time="1200",
    )

    ds, _, total, n = get_fixtures(source_name, request)

    for i in ds:
        print(i)
    assert len(ds) == 4, len(ds)

    check_sel_and_order(ds, params, levels)


@pytest.mark.parametrize("params", (["t", "u"], ["u", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
# @pytest.mark.parametrize("source_name", ["indexed-directory", "list-of-dicts"])
@pytest.mark.parametrize("source_name", ["indexed-directory"])
def test_indexing_order_by_with_keyword(params, levels, source_name):
    request = dict(variable=params, level=levels, date=20220929, time="1200")
    request["order_by"] = dict(level=levels, variable=params)

    ds, _, total, n = get_fixtures(source_name, request)

    assert len(ds) == n, len(ds)

    check_sel_and_order(ds, params, levels)


@pytest.mark.parametrize("params", (["t", "u"],))
@pytest.mark.parametrize("levels", ([500, 850],))
@pytest.mark.parametrize("source_name", ["indexed-directory", "file"])
def test_indexing_order_by_with_method_with_list(params, levels, source_name):
    request = dict(variable=params, level=levels, date=20220929, time="1200")
    order_by = ["level", "variable"]

    ds, _, total, n = get_fixtures(source_name, {})

    assert len(ds) == total, len(ds)

    ds = ds.sel(**request)
    assert len(ds) == n, len(ds)

    ds = ds.order_by(order_by)
    assert len(ds) == n

    check_sel_and_order(ds, params, levels)


@pytest.mark.parametrize("params", (["t", "u"], ["u", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
# @pytest.mark.parametrize("source_name", ["indexed-directory", "list-of-dicts", "file"])
@pytest.mark.parametrize("source_name", ["indexed-directory", "file"])
def test_indexing_order_by_with_method(params, levels, source_name):
    request = dict(variable=params, level=levels, date=20220929, time="1200")
    order_by = dict(level=levels, variable=params)

    ds, _, total, n = get_fixtures(source_name, {})

    print(ds)
    print()
    for i in ds:
        print(i)
    assert len(ds) == total, len(ds)

    ds = ds.sel(**request)
    assert len(ds) == n, len(ds)

    ds = ds.order_by(order_by)
    assert len(ds) == n

    check_sel_and_order(ds, params, levels)

    # keys = list(ds.coords.keys())
    # assert keys == ["levelist", "param"], keys
    # coords_params = list(ds.coords["param"])
    # coords_levels = list(ds.coords["levelist"])
    # coords_levels = [int(x) for x in coords_levels]
    # assert coords_params == params, (coords_params, params)
    # assert coords_levels == levels, (coords_levels, levels)


@pytest.mark.parametrize("params", (["t", "u"], ["u", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500], ["500", "850"], ["850", "500"]))
# @pytest.mark.parametrize("source_name", ["indexed-directory", "list-of-dicts", "file"])
@pytest.mark.parametrize("source_name", ["indexed-directory"])
def test_indexing_order_ascending_descending(params, levels, source_name):
    request = dict(variable=params, level=levels, date=20220929, time="1200")
    order_by = dict(level="descending", variable="ascending")

    ds, _, total, n = get_fixtures(source_name, {})

    ds = ds.sel(**request)
    assert len(ds) == 4, len(ds)

    ds = ds.order_by(order_by)
    assert len(ds) == 4

    assert ds[0].metadata("param") == min(params)
    assert ds[1].metadata("param") == max(params)
    assert ds[2].metadata("param") == min(params)
    assert ds[3].metadata("param") == max(params)

    assert int(ds[0].metadata("level")) == max([int(x) for x in levels])
    assert int(ds[1].metadata("level")) == max([int(x) for x in levels])
    assert int(ds[2].metadata("level")) == min([int(x) for x in levels])
    assert int(ds[3].metadata("level")) == min([int(x) for x in levels])
    print()


# Index files have been created with :
#  export BASEURL=https://object-store.os-api.cci1.ecmwf.int/climetlab/test-data/input/indexed-urls
#  climetlab index_gribs $BASEURL/large_grib_1.grb > large_grib_1.grb.index
#  climetlab index_gribs $BASEURL/large_grib_2.grb > large_grib_2.grb.index
#  climetlab index_gribs large_grib_1.grb large_grib_2.grb --baseurl $BASEURL > global_index.index

REQUEST_1 = {
    "domain": "g",
    "levtype": "pl",
    "levelist": "850",
    "date": "19970228",
    "time": "2300",
    "step": "0",
    "param": "r",
    "class": "ea",
    "type": "an",
    "stream": "oper",
    "expver": "0001",
    #
    "n": ["1", "2"],
}
# source = load_source(
#     "indexed-urls",
#     baseurl + "/test-data/input/indexed-urls/large_grib_{n}.grb",
#     REQUEST_1,
# )

if __name__ == "__main__":
    from climetlab.testing import main

    # test_indexing_order_by_with_request(["u", "t"], [500, 850], "list-of-dicts")
    # test_indexing_order_by_with_method(["u", "t"], [500, 850], "file")
    # test_indexing_order_by_with_method(["u", "t"], [500, 850], "indexed-directory")
    # test_indexing_order_ascending_descending(["t", "u"], [500, 850], 'file')
    # test_indexing_order_by_with_method_with_list(["t", "u"], [850, 500], 'indexed-directory')
    # test_indexing_order_by_with_method(["t", "u"], [500, 850], 'indexed-directory')

    main(__file__)
