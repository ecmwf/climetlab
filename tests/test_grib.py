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

from climetlab import load_source, plot_map


def test_plot():
    for s in load_source("file", "docs/examples/test.grib"):
        plot_map(s)

        # test.grib fields endStep is 0, so datetime == valid_datetime
        assert s.datetime() == s.valid_datetime()

        # test shape
        assert s.shape == (11, 19)


@pytest.mark.skipif(("GITHUB_WORKFLOW" in os.environ) or True, reason="Not yet ready")
def test_sel():
    s = load_source("file", "docs/examples/test.grib")

    s.sel(shortName="2t")


@pytest.mark.skipif(("GITHUB_WORKFLOW" in os.environ) or True, reason="Not yet ready")
def test_multi():
    s1 = load_source(
        "cds",
        "reanalysis-era5-single-levels",
        product_type="reanalysis",
        param="2t",
        date="2021-03-01",
    )
    s2 = load_source(
        "cds",
        "reanalysis-era5-single-levels",
        product_type="reanalysis",
        param="2t",
        date="2021-03-02",
    )
    s3 = load_source(
        "cds",
        "reanalysis-era5-single-levels",
        product_type="reanalysis",
        param="2t",
        date=["2021-03-01", "2021-03-02"],
    )
    source = load_source("multi", s1, s2)
    for s in source:
        print(s)

    source.to_xarray()

    import xarray as xr

    print(s1)
    print(s1.path)
    print(s2.path)
    print(s3.path)

    print("--------------")
    s3.to_xarray()
    print("--------------")

    xr.open_mfdataset([s1.path, s2.path], engine="cfgrib")


if __name__ == "__main__":
    test_multi()
