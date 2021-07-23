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
from climetlab.testing import climetlab_file


def test_netcdf():
    for s in load_source("file", climetlab_file("docs/examples/test.nc")):
        plot_map(s)


def test_dummy_netcdf():
    s = load_source(
        "dummy-source",
        kind="netcdf",
    )
    ds = s.to_xarray()
    assert "lat" in ds.dims


def test_dummy_netcdf_2():
    s = load_source(
        "dummy-source", kind="netcdf", dims=["lat", "lon", "time"], variables=["a", "b"]
    )
    ds = s.to_xarray()
    assert "lat" in ds.dims


def test_dummy_netcdf_3():
    s = load_source(
        "dummy-source",
        kind="netcdf",
        dims={"lat": dict(size=3), "lon": dict(size=2), "time": dict(size=2)},
        variables=["a", "b"],
    )
    ds = s.to_xarray()
    assert "lat" in ds.dims


def test_dummy_netcdf_4():
    s = load_source(
        "dummy-source",
        kind="netcdf",
        dims={"lat": dict(size=3), "lon": dict(size=2), "time": dict(size=2)},
        variables={
            "a": dict(dims=["lat", "lon"]),
            "b": dict(dims=["lat", "time"]),
        },
    )
    ds = s.to_xarray()
    assert "lat" in ds.dims


def test_multi():
    if not os.path.exists(os.path.expanduser("~/.cdsapirc")):
        pytest.skip("No ~/.cdsapirc")
    s1 = load_source(
        "cds",
        "reanalysis-era5-single-levels",
        product_type="reanalysis",
        param="2t",
        date="2021-03-01",
        format="netcdf",
    )
    s1.to_xarray()
    s2 = load_source(
        "cds",
        "reanalysis-era5-single-levels",
        product_type="reanalysis",
        param="2t",
        date="2021-03-02",
        format="netcdf",
    )
    s2.to_xarray()

    source = load_source("multi", s1, s2)
    for s in source:
        print(s)

    source.to_xarray()


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
