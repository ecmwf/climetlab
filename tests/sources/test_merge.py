#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import numpy as np
import pytest
import xarray as xr

from climetlab import load_source

# These functionalities are variations around
# http://xarray.pydata.org/en/stable/user-guide/combining.html#combining-multi


def assert_same_xarray(x, y):
    assert x.broadcast_equals(y)
    assert x.equals(y)
    assert x.identical(y)
    assert len(x) == len(y)
    assert set(x.keys()) == set(y.keys())
    assert len(x.dims) == len(y.dims)
    assert len(x.coords) == len(y.coords)
    for k in x.keys():
        xda, yda = x[k], y[k]
        assert xda.values.shape == yda.values.shape
        assert np.all(xda.values == yda.values)


def merger_func(paths_or_sources):
    return xr.open_mfdataset(paths_or_sources)


class Merger_obj:
    def to_xarray(self, paths_or_sources, **kwargs):
        return xr.open_mfdataset(paths_or_sources)


@pytest.mark.parametrize("custom_merger", (merger_func, Merger_obj()))
def test_nc_merge_custom(custom_merger):
    s1 = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=["lat", "lon", "time"],
        variables=["a", "b"],
    )
    ds1 = s1.to_xarray()

    s2 = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=["lat", "lon", "time"],
        variables=["c", "d"],
    )
    ds2 = s2.to_xarray()

    target = xr.merge([ds1, ds2])

    ds = load_source("multi", [s1, s2], merger=custom_merger)
    ds.graph()
    merged = ds.to_xarray()

    assert target.identical(merged)

    target2 = xr.open_mfdataset([s1.path, s2.path])
    assert target2.identical(merged)


def test_nc_merge_var():
    s1 = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=["lat", "lon", "time"],
        variables=["a", "b"],
    )
    ds1 = s1.to_xarray()

    s2 = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=["lat", "lon", "time"],
        variables=["c", "d"],
    )
    ds2 = s2.to_xarray()

    target = xr.merge([ds1, ds2])
    ds = load_source("multi", [s1, s2])
    ds.graph()
    merged = ds.to_xarray()

    assert target.identical(merged)

    target2 = xr.open_mfdataset([s1.path, s2.path])
    assert target2.identical(merged)


def _merge_var_different_coords(kind1, kind2):
    s1 = load_source(
        "climetlab-testing",
        kind=kind1,
        dims=["lat", "lon"],
        variables=["a", "b"],
    )
    ds1 = s1.to_xarray()

    s2 = load_source(
        "climetlab-testing",
        kind=kind2,
        dims=["lat", "time"],
        variables=["c", "d"],
    )
    ds2 = s2.to_xarray()

    target = xr.merge([ds1, ds2])
    ds = load_source("multi", [s1, s2])
    ds.graph()
    merged = ds.to_xarray()

    assert target.identical(merged)


def test_nc_merge_var_different_coords():
    _merge_var_different_coords("netcdf", "netcdf")


@pytest.mark.skipif(True, reason="Test not yet implemented")
def test_grib_merge_var_different_coords():
    _merge_var_different_coords("grib", "grib")


@pytest.mark.skipif(True, reason="Test not yet implemented")
def test_grib_nc_merge_var_different_coords():
    _merge_var_different_coords("netcdf", "grib")


def _concat_var_different_coords_1(kind1, kind2):
    s1 = load_source(
        "climetlab-testing",
        kind=kind1,
        variables=["a"],
        dims=["lat", "lon", "time"],
        coord_values=dict(time=[1, 3]),
    )
    ds1 = s1.to_xarray()

    s2 = load_source(
        "climetlab-testing",
        kind=kind2,
        variables=["a"],
        dims=["lat", "lon", "time"],
        coord_values=dict(time=[2, 4]),
    )
    ds2 = s2.to_xarray()

    target = xr.concat([ds1, ds2], dim="time")

    ds = load_source("multi", [s1, s2], merger="concat(concat_dim=time)")
    ds.graph()
    merged = ds.to_xarray()

    assert target.identical(merged), f"Contat failed for {kind1}, {kind2}"


def test_nc_concat_var_different_coords_1():
    for kind1 in ["netcdf"]:  # ["netcdf", "grib"]:
        for kind2 in ["netcdf"]:  # ["netcdf", "grib"]:
            _concat_var_different_coords_1(kind1, kind2)


def test_nc_concat_var_different_coords_2():
    s1 = load_source(
        "climetlab-testing",
        kind="netcdf",
        variables=["a"],
        dims=["lat", "lon", "time"],
        coord_values=dict(time=[2, 1]),
    )
    ds1 = s1.to_xarray()

    s2 = load_source(
        "climetlab-testing",
        kind="netcdf",
        variables=["a"],
        dims=["lat", "lon", "time"],
        coord_values=dict(time=[3, 4]),
    )
    ds2 = s2.to_xarray()

    target = xr.concat([ds1, ds2], dim="time")

    ds = load_source("multi", [s1, s2], merger="concat(concat_dim=time)")
    ds.graph()
    merged = ds.to_xarray()

    assert target.identical(merged)


def test_nc_wrong_concat_var():
    s1 = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=["lat", "lon", "time"],
        variables=["a", "b"],
        coord_values=dict(time=[1, 2]),
    )
    ds1 = s1.to_xarray()

    s2 = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=["lat", "time"],
        variables=["a", "b"],
        coord_values=dict(time=[8, 9]),
    )
    ds2 = s2.to_xarray()

    target = xr.concat([ds1, ds2], dim="time")
    ds = load_source("multi", [s1, s2], merger="concat(concat_dim=time)")

    ds.graph()
    merged = ds.to_xarray()

    assert target.identical(merged)


def get_hierarchy():
    a1 = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=["lat", "lon", "forecast_time"],
        variables=["a"],
        coord_values=dict(forecast_time=[1, 3]),
    )
    a2 = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=["lat", "lon", "forecast_time"],
        variables=["a"],
        coord_values=dict(forecast_time=[2, 4]),
    )
    b1 = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=["lat", "lon", "forecast_time"],
        variables=["b"],
        coord_values=dict(forecast_time=[1, 3]),
    )
    b2 = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=["lat", "lon", "forecast_time"],
        variables=["b"],
        coord_values=dict(forecast_time=[2, 4]),
    )

    target = xr.merge(
        [
            xr.merge([a1.to_xarray(), a2.to_xarray()]),
            xr.merge([b1.to_xarray(), b2.to_xarray()]),
        ]
    )
    return target, a1, a2, b1, b2


@pytest.mark.skipif(True, reason="Test not yet implemented")
def test_nc_concat_merge_var():
    target, a1, a2, b1, b2 = get_hierarchy()

    s = load_source(
        "multi",
        [
            load_source("multi", [a1, a2], merger="concat(dim=forecast_time)"),
            load_source("multi", [b1, b2], merger="concat(dim=forecast_time)"),
        ],
        merger="merge",
    )

    merged = s.to_xarray()
    assert target.identical(merged), merged


@pytest.mark.skipif(True, reason="Test not yet implemented")
def test_nc_merge_concat_var():
    target, a1, a2, b1, b2 = get_hierarchy()
    s = load_source(
        "multi",
        [
            load_source("multi", [a1, b1], merger="merge()"),
            load_source("multi", [a2, b2], merger="merge()"),
        ],
        merger="concat(dim=forecast_time)",
    )
    merged = s.to_xarray()
    assert target.identical(merged)


# @pytest.mark.skipif(IN_GITHUB, reason="Too long to test on GITHUB")
# @pytest.mark.external_download
# @pytest.mark.download
# def test_merge_pangeo_1():
#     _merge_pangeo(inner_merger="concat(concat_dim=time)")


# @pytest.mark.skipif(IN_GITHUB, reason="Too long to test on GITHUB")
# @pytest.mark.external_download
# @pytest.mark.download
# def test_merge_pangeo_2():
#     _merge_pangeo(inner_merger=("concat", {"concat_dim": "time"}))


# @pytest.mark.skipif(IN_GITHUB, reason="Too long to test on GITHUB")
# @pytest.mark.external_download
# @pytest.mark.download
# @pytest.mark.skipif(True, reason="Test not yet implemented")
# def test_merge_pangeo_3():
#     def preprocess(ds):
#         return ds

#     _merge_pangeo(
#         inner_merger=(
#             "simple",
#             dict(
#                 concat_dim="time",
#                 combine="nested",
#                 preprocess=preprocess,
#             ),
#         )
#     )


# def _merge_pangeo(inner_merger):
#     # Reproduce example from:
#     # https://pangeo-forge.readthedocs.io/en/latest/tutorials/terraclimate.html
#     #
#     # target_chunks = {"lat": 1024, "lon": 1024, "time": 12}
#     # only do two years to keep the example small; it's still big!
#     years = list(range(1958, 1960))
#     variables = [
#         "aet",
#         "def",
#         # "pet",
#         # "ppt",
#         # "q",
#         # "soil",
#         # "srad",
#         # "swe",
#         # "tmax",
#         # "tmin",
#         # "vap",
#         # "ws",
#         # "vpd",
#         # "PDSI",
#     ]

#     def make_filename(variable, time):
#         return (
#             "http://thredds.northwestknowledge.net:8080/"
#             "thredds/fileServer/TERRACLIMATE_ALL/data/"
#             f"TerraClimate_{variable}_{time}.nc"
#         )

#     def preprocess(ds):
#         return ds

#     dslist_v = []
#     xdslist_v = []
#     for variable in variables:
#         dslist_t = []
#         xdslist_t = []

#         for year in years:
#             url = make_filename(variable, year)
#             s = load_source("url", url)
#             dslist_t.append(s)
#             xdslist_t.append(s.to_xarray())

#         xds = xr.concat(xdslist_t, dim="time")
#         xdslist_v.append(xds)

#         ds = load_source(
#             "multi",
#             dslist_t,
#             merger=inner_merger,
#         )
#         dslist_v.append(ds)

#     target = xr.merge(xdslist_v)

#     source = load_source("multi", dslist_v, merger="merge()")

#     source.graph()

#     ds = source.to_xarray()

#     slicer = slice(0, 100)
#     ds = ds.isel(lat=slicer, lon=slicer)
#     target = target.isel(lat=slicer, lon=slicer)
#     assert ds.identical(target), ds


if __name__ == "__main__":
    # test_merge_pangeo_1()
    from climetlab.testing import main

    main(__file__)
