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
import shutil
import time
import warnings

import pytest

import climetlab as cml
from climetlab.core.temporary import temp_directory, temp_file
from climetlab.decorators import normalize
from climetlab.indexing import PerUrlIndex
from climetlab.readers.grib.index import FieldSet
from climetlab.testing import climetlab_file
from climetlab.utils.serialise import SERIALISATION, deserialise_state, serialise_state

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


class GribIndexFromDicts(FieldSet):
    def __init__(self, list_of_dicts, *args, **kwargs):
        self.list_of_dicts = list_of_dicts
        super().__init__(*args, **kwargs)

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


def get_fixtures_directory(request):
    tmp = dir_with_grib_files()
    total, n = 6, 4
    ds = cml.load_source("directory", tmp.path, **request)
    return ds, tmp, total, n


def get_fixtures_file(request):
    tmp = unique_grib_file()
    total, n = 6, 4
    ds = cml.load_source("file", tmp.path, **request)
    return ds, tmp, total, n


def get_fixtures_list_of_dicts(request):
    tmp = list_of_dicts()
    total, n = 6, 4
    ds = GribIndexFromDicts(tmp, **request)
    ds = ds.mutate()
    return ds, tmp, total, n


def get_fixtures(source_name, *args, **kwargs):
    return {
        "directory": get_fixtures_directory,
        "file": get_fixtures_file,
        "list-of-dicts": get_fixtures_list_of_dicts,
    }[source_name](*args, **kwargs)


def check_sel_and_order(ds, params, levels):
    assert ds[0].metadata("param") == params[0]
    assert ds[1].metadata("param") == params[1]
    assert ds[2].metadata("param") == params[0]
    assert ds[3].metadata("param") == params[1]

    assert ds[0].metadata("level") == levels[0]
    assert ds[1].metadata("level") == levels[0]
    assert ds[2].metadata("level") == levels[1]
    assert ds[3].metadata("level") == levels[1]