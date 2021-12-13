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

from climetlab.indexing.backends import JsonIndexBackend

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
    return JsonIndexBackend(index_jsonl)


def test_indexing_json_1(backend):
    parts = backend.lookup(REQUEST_1)
    assert len(parts) == 1
    assert parts[0][0] == "data/02.grb"
    assert parts[0][1][0] == 94156098
    assert parts[0][1][1] == 23358


def test_indexing_json_2(backend):
    parts = backend.lookup(REQUEST_2)
    assert len(parts) == 1


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
