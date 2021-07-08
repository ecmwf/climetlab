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


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
