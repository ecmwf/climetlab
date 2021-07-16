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

import numpy as np
import pytest
import xarray as xr

from climetlab import load_source
from climetlab.core.temporary import temp_directory


def assert_same_xarray(x, y):
    assert len(x) == len(y)
    assert len(x.dims) == len(y.dims)
    assert set(x.keys()) == set(y.keys())
    assert len(x.dims) == len(y.dims)
    assert len(x.coords) == len(y.coords)
    for k in x.keys():
        xda, yda = x[k], y[k]
        assert xda.values.shape == yda.values.shape
        assert np.all(xda.values == yda.values)


def test_merge_netcdf_merge_var():
    with temp_directory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, "s1"))
        s1 = load_source(
            "dummy-source",
            kind="netcdf",
            dims=["lat", "lon", "time"],
            variables=["a", "b"],
        )
        s1.save(os.path.join(tmpdir, "s1", "s1.netcdf"))
        ds1 = s1.to_xarray()

        os.mkdir(os.path.join(tmpdir, "s2"))
        s2 = load_source(
            "dummy-source",
            kind="netcdf",
            dims=["lat", "lon", "time"],
            variables=["c", "d"],
        )
        s2.save(os.path.join(tmpdir, "s2", "s2.netcdf"))
        ds2 = s2.to_xarray()

        target = xr.merge([ds1, ds2])
        ds = load_source("multi", [s1, s2])
        ds.graph()
        merged = ds.to_xarray()

        assert_same_xarray(target, merged)


def test_merge_netcdf_merge_var_different_coords():
    with temp_directory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, "s1"))
        s1 = load_source(
            "dummy-source", kind="netcdf", dims=["lat", "lon"], variables=["a", "b"]
        )
        s1.save(os.path.join(tmpdir, "s1", "s1.netcdf"))
        ds1 = s1.to_xarray()

        os.mkdir(os.path.join(tmpdir, "s2"))
        s2 = load_source(
            "dummy-source", kind="netcdf", dims=["lat", "time"], variables=["c", "d"]
        )
        s2.save(os.path.join(tmpdir, "s2", "s2.netcdf"))
        ds2 = s2.to_xarray()

        target = xr.merge([ds1, ds2])
        ds = load_source("multi", [s1, s2])
        ds.graph()
        merged = ds.to_xarray()

        assert_same_xarray(target, merged)


def test_merge_netcdf_concat_var_different_coords():
    with temp_directory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, "s1"))
        s1 = load_source(
            "dummy-source",
            kind="netcdf",
            dims=["lat", "lon"],
            variables=["a", "b"],
            coord_values=dict(lat=[1, 2]),
        )
        s1.save(os.path.join(tmpdir, "s1", "s1.netcdf"))
        ds1 = s1.to_xarray()

        os.mkdir(os.path.join(tmpdir, "s2"))
        s2 = load_source(
            "dummy-source",
            kind="netcdf",
            dims=["lat", "lon"],
            variables=["a", "b"],
            coord_values=dict(lat=[8, 9]),
        )
        s2.save(os.path.join(tmpdir, "s2", "s2.netcdf"))
        ds2 = s2.to_xarray()

        target = xr.concat([ds1, ds2], dim="lat")
        ds = load_source("multi", [s1, s2])
        ds.graph()
        merged = ds.to_xarray()

        assert_same_xarray(target, merged)


@pytest.mark.skipif(True, reason="Test not yet implemented")
def test_merge_netcdf_wrong_concat_var():
    with temp_directory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, "s1"))
        s1 = load_source(
            "dummy-source",
            kind="netcdf",
            dims=["lat", "lon"],
            variables=["a", "b"],
            coord_values=dict(lat=[1, 2]),
        )
        s1.save(os.path.join(tmpdir, "s1", "s1.netcdf"))
        ds1 = s1.to_xarray()

        os.mkdir(os.path.join(tmpdir, "s2"))
        s2 = load_source(
            "dummy-source",
            kind="netcdf",
            dims=["lat"],
            variables=["a", "b"],
            coord_values=dict(lat=[8, 9]),
        )
        s2.save(os.path.join(tmpdir, "s2", "s2.netcdf"))
        ds2 = s2.to_xarray()

        target = xr.concat([ds1, ds2], dim="lat")
        print(target)
        ds = load_source("multi", [s1, s2])
        ds.graph()
        merged = ds.to_xarray()

        assert_same_xarray(target, merged)


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
