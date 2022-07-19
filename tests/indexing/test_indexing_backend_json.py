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

from climetlab.readers.grib.index import JsonIndex

index_jsonl = os.path.join(os.path.dirname(__file__), "index.jsonl")

REQUEST_1 = {
    "domain": "g",
    "levtype": "pl",
    "levelist": "850",
    "date": "19970228",
    "time": "2300",
    "step": "0",
    "param": "157.128",
    "class": "ea",
    "type": "an",
    "stream": "oper",
    "expver": "0001",
}

REQUEST_2 = {
    "domain": "g",
    "levtype": "pl",
    "levelist": "500",
    "date": "19970101",
    "time": "0000",
    "step": "0",
    "param": "129.128",
    "class": "ea",
    "type": "an",
    "stream": "oper",
    "expver": "0001",
}


@pytest.fixture
def backend():
    return JsonIndex.from_existing_db(index_jsonl)


def test_indexing_json_1(backend):
    s = backend.sel(REQUEST_1)
    assert s.number_of_parts() == 1
    p = s.part(0)
    assert p.path == "data/02.grb"
    assert p.offset == 94156098
    assert p.length == 23358


def test_indexing_json_2(backend):
    s = backend.sel(REQUEST_2)
    assert s.number_of_parts() == 1


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
