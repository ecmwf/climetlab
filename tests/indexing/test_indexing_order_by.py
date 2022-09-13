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
import time

import pytest

import climetlab as cml
from climetlab.core.temporary import temp_directory, temp_file
from climetlab.decorators import normalize
from climetlab.indexing import PerUrlIndex
from climetlab.readers.grib.index import GribIndexFromDicts
from climetlab.testing import climetlab_file

CML_BASEURL_S3 = "https://storage.ecmwf.europeanweather.cloud/climetlab"
CML_BASEURL_CDS = "https://datastore.copernicus-climate.eu/climetlab"
CML_BASEURL_GET = "https://get.ecmwf.int/repository/test-data/climetlab"
CML_BASEURLS = [CML_BASEURL_S3, CML_BASEURL_GET, CML_BASEURL_CDS]


TEST_GRIB_FILES = [
    climetlab_file(p)
    for p in [
        "docs/examples/test.grib",
        "docs/examples/test4.grib",
    ]
]


def dir_with_grib_files():
    tmp = temp_directory()
    _build_dir_with_grib_files(tmp.path)
    return tmp


def _build_dir_with_grib_files(testdir):
    os.makedirs(testdir, exist_ok=True)
    for path in TEST_GRIB_FILES:
        shutil.copy(path, testdir)


def unique_grib_file():
    tmp = temp_file()
    _build_unique_grib_file(tmp.path)
    return tmp


def _build_unique_grib_file(path):
    with open(path, mode="wb") as target:
        for file in TEST_GRIB_FILES:
            with open(file, mode="rb") as f:
                shutil.copyfileobj(f, target)


def list_of_dicts():
    return [
        {
            "gridType": "regular_ll",
            "Nx": 2,
            "Ny": 3,
            "distinctLatitudes": [-10.0, 0.0, 10.0],
            "distinctLongitudes": [0.0, 10.0],
            "paramId": 167,
            "shortName": "2t",
            "time": "1000",
            "level": "500",
            "values": [[1, 2], [3, 4], [5, 6]],
        },
        {
            "gridType": "regular_ll",
            "Nx": 2,
            "Ny": 3,
            "distinctLatitudes": [-10.0, 0.0, 10.0],
            "distinctLongitudes": [0.0, 10.0],
            "paramId": 167,
            "shortName": "2t",
            "time": "1200",
            "level": "500",
            "values": [[2, 2], [4, 4], [6, 6]],
        },
        {
            "gridType": "regular_ll",
            "Nx": 2,
            "Ny": 3,
            "distinctLatitudes": [-10.0, 0.0, 10.0],
            "distinctLongitudes": [0.0, 10.0],
            "paramId": 168,
            "shortName": "2d",
            "level": "850",
            "values": [[18, 2], [3, 4], [5, 6]],
        },
    ]


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
@pytest.mark.parametrize("source_name", ["directory"])
def test_indexing_order_by_with_request(params, levels, source_name):
    request = dict(
        level=levels,
        variable=params,
        date=20070101,
        time="1200",
    )

    if source_name == "directory":
        tmp = dir_with_grib_files()
        ds = cml.load_source(source_name, tmp.path, **request)
    elif source_name == "file":
        tmp = unique_grib_file()
        ds = cml.load_source(source_name, tmp.path, **request)

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
    print()


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
@pytest.mark.parametrize(
    "source_name",
    [
        "directory",
    ],
)
def test_indexing_order_by_with_keyword(params, levels, source_name):
    request = dict(
        variable=params,
        level=levels,
        date=20070101,
        time="1200",
    )
    order_by = dict(
        level=levels,
        variable=params,
    )

    if source_name == "directory":
        tmp = dir_with_grib_files()
    elif source_name == "file":
        tmp = unique_grib_file()

    ds = cml.load_source(source_name, tmp.path, order_by=order_by, **request)
    assert len(ds) == 4, len(ds)
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
    print()


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
@pytest.mark.parametrize(
    "source_name",
    [
        "directory",
        "list-of-dicts",
        "file",
    ],
)
def test_indexing_order_by_with_method(params, levels, source_name):
    request = dict(
        variable=params,
        level=levels,
        date=20070101,
        time="1200",
    )

    order_by = dict(level=levels, variable=params)

    if source_name == "directory":
        tmp = dir_with_grib_files()
        total, n = 6, 4
        ds = cml.load_source(source_name, tmp.path)
    elif source_name == "file":
        tmp = unique_grib_file()
        total, n = 6, 4
        ds = cml.load_source(source_name, tmp.path)
    elif source_name == "list-of-dicts":
        tmp = list_of_dicts()
        total, n = 3, 2
        ds = GribIndexFromDicts(tmp)

    assert len(ds) == total, len(ds)

    ds = ds.sel(**request)
    assert len(ds) == n, len(ds)
    ds = ds.order_by(order_by)
    for i in ds:
        print(i)
    assert len(ds) == n

    assert ds[0].metadata("short_name") == params[0]
    assert ds[1].metadata("short_name") == params[1]
    assert ds[2].metadata("short_name") == params[0]
    assert ds[3].metadata("short_name") == params[1]

    assert ds[0].metadata("level") == levels[0]
    assert ds[1].metadata("level") == levels[0]
    assert ds[2].metadata("level") == levels[1]
    assert ds[3].metadata("level") == levels[1]
    print()


@pytest.mark.parametrize("params", (["t", "z"],))
@pytest.mark.parametrize("levels", ([500, 850],))
@pytest.mark.parametrize(
    "source_name",
    [
        "directory",
        # "file",
    ],
)
def test_indexing_order_ascending_descending(params, levels, source_name):
    request = dict(
        variable=params,
        level=levels,
        date=20070101,
        time="1200",
    )

    order_by = dict(level="descending", variable="ascending")

    if source_name == "directory":
        tmp = dir_with_grib_files()
    elif source_name == "file":
        tmp = unique_grib_file()

    ds = cml.load_source(source_name, tmp.path)
    ds = ds.sel(**request)
    assert len(ds) == 4, len(ds)
    ds = ds.order_by(order_by)
    for i in ds:
        print(i)
    assert len(ds) == 4

    assert ds[0].metadata("short_name") == params[0]
    assert ds[1].metadata("short_name") == params[1]
    assert ds[2].metadata("short_name") == params[0]
    assert ds[3].metadata("short_name") == params[1]

    assert ds[0].metadata("level") == levels[1]
    assert ds[1].metadata("level") == levels[1]
    assert ds[2].metadata("level") == levels[0]
    assert ds[3].metadata("level") == levels[0]
    print()


# Index files have been created with :
#  export BASEURL=https://storage.ecmwf.europeanweather.cloud/climetlab/test-data/input/indexed-urls
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

    test_indexing_order_by_with_method(["t", "z"], [500, 850], "file")
    # test_indexing_order_ascending_descending(["t", "z"], [500, 850], 'file')

#    main(__file__)
