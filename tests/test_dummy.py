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
from utils import modules_installed

from climetlab import load_source


@pytest.mark.skipif(not modules_installed("zarr"), reason="Zarr not installed")
def test_dummy_zarr():
    s = load_source(
        "dummy-source",
        kind="zarr",
    )
    print(s)
    ds = s.to_xarray()
    assert "lat" in ds.dims


@pytest.mark.skipif(not modules_installed("zarr"), reason="Zarr not installed")
def test_dummy_zarr_zip():
    s = load_source(
        "dummy-source",
        kind="zarr-zip",
    )
    print(s)
    ds = s.to_xarray()
    assert "lat" in ds.dims


def test_dummy_netcdf():
    s = load_source(
        "dummy-source",
        kind="netcdf",
    )
    ds = s.to_xarray()
    print(ds)
    assert "lat" in ds.dims


def test_dummy_grib():
    s = load_source(
        "dummy-source",
        kind="grib",
        paramId=[129, 130],
        date=[19900101, 19900102],
        level=[1000, 500],
    )
    assert len(s) == 8


if __name__ == "__main__":
    from utils import main

    main(globals())
