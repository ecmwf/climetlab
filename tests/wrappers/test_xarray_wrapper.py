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
from climetlab import load_source
from climetlab.wrappers.xarray import find_lat_lon

# def checksum_of_plot_map(ds):
#     from climetlab.core.temporary import temp_file
#     with temp_file(extension=".png") as filename:
#         cml.plot_map(ds, path=filename)
#         with open(filename, "rb") as f:
#             return f.read()


@pytest.mark.parametrize(
    "coords",
    [
        "lat,lon",
        "lon,lat",
        "time,Latitude,Longitude",
        "other,lat,lon",
        "time,lat,lon",
        "lat,lon,time",
        "LAT,lon",
        "LatitudE,LONgitUDE",
    ],
)
def test_wrapper_xarray_plot_map(coords):
    source = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=coords.split(","),
    )
    ds = source.to_xarray()

    lat, lon = find_lat_lon(ds)
    assert lat.name is not None
    assert lon.name is not None

    cml.plot_map(ds)


@pytest.mark.parametrize(
    "coords",
    [
        "other,custom,lon",
        "other,custom2,custom",
        "custom,custom2,time",
        "lat,time,time2,custom2",
    ],
)
def test_wrapper_xarray_plot_map_2(coords):
    source = load_source(
        "climetlab-testing",
        kind="netcdf",
        dims=coords.split(","),
    )
    ds = source.to_xarray()

    if "custom" in ds.keys():
        ds["custom"].attrs["long_name"] = "latitude"
    if "custom2" in ds.keys():
        ds["custom2"].attrs["standard_name"] = "longitude"

    lat, lon = find_lat_lon(ds)
    assert lat is not None
    assert lon is not None

    cml.plot_map(ds)


def test_plot_map_grib():
    source = load_source("climetlab-testing", kind="grib", date=20000101)
    cml.plot_map(source)


def test_wrapper_xarray_grib():
    source = load_source("climetlab-testing", kind="grib", date=20000101)
    ds = source.to_xarray()

    lat, lon = find_lat_lon(ds)
    assert lat is not None
    assert lon is not None

    cml.plot_map(ds)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
