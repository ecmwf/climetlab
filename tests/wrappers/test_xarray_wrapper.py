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


def checksum_of_plot_map(ds):
    with temp_file(extension=".png") as filename:
        cml.plot_map(ds, path=filename)
        with open(filename, "rb") as f:
            return f.read()


def get_reference_checksum():
    source = load_source(
        "dummy-source",
        kind="netcdf",
        dims=["lat", "lon"],
    )
    ds = source.to_xarray()
    return checksum_of_plot_map(ds)


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
        "other,custom_lat,lon",
        "other,custom_lon,custom_lat",
        "custom_lat,custom_lon,time",
        "lat,time,time2,custom_lon",
    ],
)
def dont_test_wrapper_xarray_plot_map(coords):
    source = load_source(
        "dummy-source",
        kind="netcdf",
        dims=coords.split(","),
    )
    ds = source.to_xarray()

    if "custom_lat" in ds.keys():
        ds["custom_lat"].attrs["long_name"] = "latitude"
    if "custom_lon" in ds.keys():
        ds["custom_lon"].attrs["standard_name"] = "longitude"

    lat, lon = find_lat_lon(ds)
    assert lat is not None
    assert lon is not None

    cml.plot_map(ds)

    # checksum not good.
    # check = checksum_of_plot_map(ds)
    # assert check == CHECK, f'Image from xr.dataset is different from reference'

    # with temp_file() as filename:
    #     ds.to_netcdf(filename)
    #     source = load_source("file", filename)
    #     with temp_file(extension='.png') as imagefile:
    #         check = checksum_of_plot_map(source)
    #         assert check == CHECK, f'Image from netcdf is different from reference'


@pytest.mark.skip(True, reason="Checksum on image not implemented")
def dont_test_check_cheksum():
    for i in range(10):
        assert get_reference_checksum() == get_reference_checksum(), "Checksum not ok"


@pytest.mark.skip(True, reason="Currently failing for grib")
def dont_test_plot_map_grib():
    source = load_source("dummy-source", kind="grib", date=20000101)
    cml.plot_map(source)


def test_wrapper_xarray_grib():
    source = load_source("dummy-source", kind="grib", date=20000101)
    ds = source.to_xarray()

    lat, lon = find_lat_lon(ds)
    assert lat is not None
    assert lon is not None

    cml.plot_map(ds)


if __name__ == "__main__":
    from climetlab.testing import main

    # test_wrapper_xarray_plot_map("lat,lon")
    # test_wrapper_xarray_plot_map("time,lat,lon")
    # print("ok")
    # test_wrapper_xarray_plot_map("lat,lon,time")

    main(__file__)
