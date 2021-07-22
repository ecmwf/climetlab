#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import mimetypes

import pytest

import climetlab as cml
from climetlab.testing import modules_installed


def test_csv_1():
    s = cml.load_source(
        "dummy-source",
        "csv",
        headers=["a", "b", "c"],
        lines=[
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ],
    )

    print(s.to_pandas())


def test_csv_2():
    s = cml.load_source(
        "dummy-source",
        "csv",
        headers=["a", "b", "c"],
        lines=[
            [1, None, 3],
            [4, 5, 6],
            [7, 8, 9],
        ],
    )

    print(s.to_pandas())


def test_csv_3():
    s = cml.load_source(
        "dummy-source",
        "csv",
        headers=["a", "b", "c"],
        lines=[
            [1, "x", 3],
            [4, "y", 6],
            [7, "z", 9],
        ],
    )

    print(s.to_pandas())


def test_csv_4():
    s = cml.load_source(
        "dummy-source",
        "csv",
        headers=["a", "b", "c"],
        quote_strings=True,
        lines=[
            [1, "x", 3],
            [4, "y", 6],
            [7, "z", 9],
        ],
    )

    print(s.to_pandas())


@pytest.mark.skipif(
    not modules_installed("tensorflow"),
    reason="Tensorflow not installed",
)
def test_csv_tfdataset():
    s = cml.load_source(
        "dummy-source",
        "csv",
        headers=["lat", "lon", "value"],
        lines=[
            [1, 0, 3],
            [0, 1, 6],
        ],
    )

    ds = s.to_tfdataset()
    print(ds)


@pytest.mark.skipif(True, reason="Test not yet implemented")
def test_csv_icoads():

    r = {
        "class": "e2",
        "date": "1662-10-01/to/1663-12-31",
        "dataset": "icoads",
        "expver": "1608",
        "groupid": "17",
        "reportype": "16008",
        "format": "ascii",
        "stream": "oper",
        "time": "all",
        "type": "ofb",
    }

    source = cml.load_source("mars", **r)
    print(source)


def test_csv_text():

    s = cml.load_source(
        "dummy-source",
        "csv",
        headers=["a", "b", "c"],
        quote_strings=True,
        lines=[
            [1, "x", 3],
            [4, "y", 6],
            [7, "z", 9],
        ],
        extension=".txt",
    )

    print(s.to_pandas())


def test_csv_mimetypes():
    assert mimetypes.guess_type("x.csv") == ("text/csv", None)
    assert mimetypes.guess_type("x.csv.gz") == ("text/csv", "gzip")
    assert mimetypes.guess_type("x.csv.bz2") == ("text/csv", "bzip2")


# TODO test compression

if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
