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
from climetlab.core.temporary import temp_file
from climetlab.wrappers.xarray import find_lat_lon


@pytest.mark.parametrize(
    "initial_format",
    [
        #        "grib",
        "netcdf",
    ],
)
@pytest.mark.parametrize(
    "coords",
    [
        "lat,lon",
        "other,lat,lon",
        "time,lat,lon",
        "lat,lon,time",
        "LAT,lon",
        "LatitudE,LONgitUDE",
        "other,unknown_lat,lon",
        "unknown_lat,unknown_lon,time",
        "lat,time,time2,unknown_lon",
    ],
)
def test_wrapper_xarray_plot_map(coords, initial_format):
    source = load_source(
        "dummy-source",
        kind=initial_format,
        dims=coords.split(","),
    )
    ds = source.to_xarray()

    if "unknown_lat" in ds.keys():
        ds["unknown_lat"].attrs["long_name"] = "latitude"
    if "unknown_lon" in ds.keys():
        ds["unknown_lon"].attrs["standard_name"] = "longitude"

    lat, lon = find_lat_lon(ds)
    assert lat is not None
    assert lon is not None

    cml.plot_map(ds)

    with temp_file() as filename:
        ds.to_netcdf(filename)
        source = load_source("file", filename)
        cml.plot_map(source)


@pytest.mark.skip("Currently failing")
def test_wrapper_xarray2():
    source = load_source(
        "dummy-source",
        kind="grib",
        dims=["other", "lat", "lon"],
    )
    ds = source.to_xarray()

    lat, lon = find_lat_lon(ds)
    assert lat is not None
    assert lon is not None

    cml.plot_map(ds)
