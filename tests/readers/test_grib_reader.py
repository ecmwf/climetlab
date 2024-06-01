#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import os

import pytest

from climetlab import load_source
from climetlab import plot_map
from climetlab.testing import NO_CDS
from climetlab.testing import climetlab_file


def test_plot():
    for s in load_source("file", climetlab_file("docs/examples/test.grib")):
        plot_map(s)

        # test.grib fields endStep is 0, so datetime == valid_datetime
        assert s.datetime() == s.valid_datetime()

        # test shape
        assert s.shape == (11, 19)


@pytest.mark.skipif(("GITHUB_WORKFLOW" in os.environ) or True, reason="Not yet ready")
def test_sel():
    s = load_source("file", climetlab_file("docs/examples/test.grib"))

    s.sel(shortName="2t")


@pytest.mark.long_test
# @pytest.mark.skipif(("GITHUB_WORKFLOW" in os.environ) or True, reason="Not yet ready")
@pytest.mark.skipif(NO_CDS, reason="No access to CDS")
def test_multi():
    s1 = load_source(
        "cds",
        "reanalysis-era5-single-levels",
        product_type="reanalysis",
        param="2t",
        date="2021-03-01",
    )
    print(s1.to_xarray())

    s2 = load_source(
        "cds",
        "reanalysis-era5-single-levels",
        product_type="reanalysis",
        param="2t",
        date="2021-03-02",
    )
    print(s2.to_xarray())

    source = load_source("multi", s1, s2)
    for s in source:
        print(s)

    source.to_xarray()


def test_dummy_grib():
    s = load_source(
        "climetlab-testing",
        kind="grib",
        paramId=[129, 130],
        date=[19900101, 19900102],
        level=[1000, 500],
    )
    assert len(s) == 8


def test_datetime():
    s = load_source("file", climetlab_file("docs/examples/test.grib"))

    assert s.to_datetime() == datetime.datetime(2020, 5, 13, 12), s.to_datetime()

    assert s.to_datetime_list() == [datetime.datetime(2020, 5, 13, 12)], s.to_datetime_list()

    s = load_source(
        "climetlab-testing",
        kind="grib",
        paramId=[129, 130],
        date=[19900101, 19900102],
        level=[1000, 500],
    )
    assert s.to_datetime_list() == [
        datetime.datetime(1990, 1, 1, 12, 0),
        datetime.datetime(1990, 1, 2, 12, 0),
    ], s.to_datetime_list()


def test_bbox():
    s = load_source("file", climetlab_file("docs/examples/test.grib"))
    assert s.to_bounding_box().as_tuple() == (73, -27, 33, 45), s.to_bounding_box()


if __name__ == "__main__":
    from climetlab.testing import main

    main()
