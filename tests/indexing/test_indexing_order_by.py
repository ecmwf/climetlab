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
import warnings

import pytest

import climetlab as cml
from climetlab.core.temporary import temp_directory, temp_file
from climetlab.decorators import normalize
from climetlab.indexing import PerUrlIndex
from climetlab.readers.grib.index import GribIndex
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
    prototype = {
        "gridType": "regular_ll",
        "Nx": 2,
        "Ny": 3,
        "distinctLatitudes": [-10.0, 0.0, 10.0],
        "distinctLongitudes": [0.0, 10.0],
        "_param_id": 167,
        "time": "1000",
        "values": [[1, 2], [3, 4], [5, 6]],
        "date": "20070101",
        "time": "1200",
    }
    return [
        {"param": "t", "levelist": 500, **prototype},
        {"param": "t", "levelist": 850, **prototype},
        {"param": "z", "levelist": 500, **prototype},
        {"param": "z", "levelist": 850, **prototype},
        {"param": "d", "levelist": 850, **prototype},
        {"param": "d", "levelist": 600, **prototype},
    ]


class GribIndexFromDicts(GribIndex):
    def __init__(self, list_of_dicts):
        self.list_of_dicts = list_of_dicts

    def __getitem__(self, n):
        class VirtualGribField(dict):
            def metadata(_self, n):
                try:
                    if n == "level":
                        n = "levelist"
                    if n == "shortName":
                        n = "param"
                    if n == "paramId":
                        n = "_param_id"
                    return _self[n]
                except KeyError:
                    warnings.warn(f"Cannot find all metadata keys.")

            @property
            def values(self, n):
                return self["values"]

        return VirtualGribField(self.list_of_dicts[n])

    def __len__(self):
        return len(self.list_of_dicts)


@pytest.mark.parametrize("params", (["t", "z"], ["z", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
@pytest.mark.parametrize(
    "source_name",
    [
        "directory",
        "file",
        "list-of-dicts",
    ],
)
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
    if source_name == "file":
        tmp = unique_grib_file()
        ds = cml.load_source(source_name, tmp.path, **request)
    if source_name == "list-of-dicts":
        tmp = list_of_dicts()
        ds = GribIndexFromDicts(tmp)

    for i in ds:
        print(i)
    assert len(ds) == 4
    assert ds[0].metadata("param") == params[0]
    assert ds[1].metadata("param") == params[1]
    assert ds[2].metadata("param") == params[0]
    assert ds[3].metadata("param") == params[1]

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
        "file",
        "list-of-dicts",
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
        ds = cml.load_source(source_name, tmp.path, order_by=order_by, **request)
    elif source_name == "file":
        tmp = unique_grib_file()
        ds = cml.load_source(source_name, tmp.path, order_by=order_by, **request)
    if source_name == "list-of-dicts":
        tmp = list_of_dicts()
        ds = GribIndexFromDicts(tmp, order_by=order_by, **request)

    assert len(ds) == 4, len(ds)
    for i in ds:
        print(i)
    assert len(ds) == 4

    assert ds[0].metadata("param") == params[0]
    assert ds[1].metadata("param") == params[1]
    assert ds[2].metadata("param") == params[0]
    assert ds[3].metadata("param") == params[1]

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
        total, n = 6, 4
        ds = GribIndexFromDicts(tmp)

    assert len(ds) == total, len(ds)

    ds = ds.sel(**request)
    for i in ds:
        print(i)
    assert len(ds) == n, len(ds)
    ds = ds.order_by(order_by)
    assert len(ds) == n
    print("-----")
    for i in ds:
        print(i)

    assert ds[0].metadata("param") == params[0]
    assert ds[1].metadata("param") == params[1]
    assert ds[2].metadata("param") == params[0]
    assert ds[3].metadata("param") == params[1]

    assert ds[0].metadata("level") == levels[0]
    assert ds[1].metadata("level") == levels[0]
    assert ds[2].metadata("level") == levels[1]
    assert ds[3].metadata("level") == levels[1]


@pytest.mark.parametrize("params", (["t", "z"],))
@pytest.mark.parametrize("levels", ([500, 850],))
@pytest.mark.parametrize(
    "source_name",
    [
        "directory",
        "file",
        "list-of-dicts",
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
        ds = cml.load_source(source_name, tmp.path)
    if source_name == "file":
        tmp = unique_grib_file()
        ds = cml.load_source(source_name, tmp.path)
    elif source_name == "list-of-dicts":
        tmp = list_of_dicts()
        ds = GribIndexFromDicts(tmp)

    ds = ds.sel(**request)
    assert len(ds) == 4, len(ds)
    ds = ds.order_by(order_by)
    for i in ds:
        print(i)
    assert len(ds) == 4

    assert ds[0].metadata("param") == params[0]
    assert ds[1].metadata("param") == params[1]
    assert ds[2].metadata("param") == params[0]
    assert ds[3].metadata("param") == params[1]

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

    test_indexing_order_by_with_method(["z", "t"], [500, 850], "list-of-dicts")
    test_indexing_order_by_with_method(["z", "t"], [500, 850], "file")
    test_indexing_order_by_with_method(["z", "t"], [500, 850], "directory")
    # test_indexing_order_ascending_descending(["t", "z"], [500, 850], 'file')

#    main(__file__)
