#!/usr/bin/env python3

# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

import pytest

import climetlab as cml
from climetlab.testing import MISSING
from climetlab.testing import climetlab_file

LOG = logging.getLogger(__name__)


@pytest.mark.skipif(MISSING("metview"), reason="Metview not installed")
def test_metview_grib():
    s = cml.load_source("file", climetlab_file("docs/examples/test.grib"))
    fs = s.to_metview()

    assert fs.url() == s.path


@pytest.mark.skipif(MISSING("metview"), reason="Metview not installed")
def test_metview_netcdf():
    s = cml.load_source("file", climetlab_file("docs/examples/test.nc"))
    fs = s.to_metview()

    assert fs.url() == s.path


@pytest.mark.skipif(MISSING("metview"), reason="Metview not installed")
def test_metview_csv():
    s = cml.load_source(
        "climetlab-testing",
        "csv",
        headers=["a", "b", "c"],
        lines=[
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ],
    )
    fs = s.to_metview()

    assert fs.url() == s.path


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
