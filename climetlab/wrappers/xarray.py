# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import itertools

import numpy as np

from climetlab.utils.dates import to_datetime_list
from climetlab.wrappers import Wrapper


def find_lat_lon(data, variable=None):

    latitude = None
    longitude = None

    LATITUDES = [
        lambda name, v: v.attrs.get("standard_name") == "latitude",
        # lambda name, v: v.attrs.get("standard_name") == "projection_x_coordinate",
        lambda name, v: v.attrs.get("long_name") == "latitude",
        lambda name, v: v.attrs.get("long_name") == "projection_x_coordinate",
        lambda name, v: name.lower() in ["latitude", "lat"],
    ]

    LONGITUDES = [
        lambda name, v: v.attrs.get("standard_name") == "longitude",
        # lambda name, v: v.attrs.get("standard_name") == "projection_y_coordinate",
        lambda name, v: v.attrs.get("long_name") == "longitude",
        lambda name, v: v.attrs.get("long_name") == "projection_y_coordinate",
        lambda name, v: name.lower() in ["longitude", "lon"],
    ]

    for trigger in LATITUDES:
        for name, v in itertools.chain(data.coords.items(), data.data_vars.items()):
            if latitude is None and trigger(name, v):
                latitude = v

    for trigger in LONGITUDES:
        for name, v in itertools.chain(data.coords.items(), data.data_vars.items()):
            if longitude is None and trigger(name, v):
                longitude = v

    # Else, use latest coordinates from the variable
    if latitude is None or longitude is None and variable is not None:
        assert latitude is None and longitude is None, (latitude, longitude)

        lat, lon = variable.dims[-2], variable.dims[-1]
        latitude = data[lat]
        longitude = data[lon]

    assert latitude.name != longitude.name, latitude.name

    return latitude, longitude


class XArrayDatasetWrapper(Wrapper):
    def __init__(self, data):

        self.data = data
        dims = 0
        for name, var in data.data_vars.items():
            # Choose variable with the most dimensions
            if len(var.dims) > dims:
                self.name = name
                self.var = var
                dims = len(var.dims)

        self.latitude, self.longitude = find_lat_lon(self.data, self.var)

        # For Magics
        self.latitude.attrs["standard_name"] = "latitude"
        self.longitude.attrs["standard_name"] = "longitude"

        self.north = np.amax(self.latitude.data)
        self.south = np.amin(self.latitude.data)
        self.east = np.amax(self.longitude.data)
        self.west = np.amin(self.longitude.data)

    def plot_map(self, backend):
        backend.bounding_box(
            north=self.north, south=self.south, west=self.west, east=self.east
        )

        dimension_settings = dict()

        extra_dims = list(self.var.dims[:])
        assert self.latitude.name in extra_dims, (self.latitude.name, extra_dims)
        extra_dims.remove(self.latitude.name)
        assert self.longitude.name in extra_dims, (self.longitude.name, extra_dims)
        extra_dims.remove(self.longitude.name)

        for d in extra_dims:
            dimension_settings[d] = 0  # self.data[d].data[0]

        assert self.data[self.latitude.name].attrs["standard_name"] == "latitude"
        assert self.data[self.longitude.name].attrs["standard_name"] == "longitude"

        backend.plot_xarray(self.data, self.name, dimension_settings)

    def field_metadata(self):
        shape = self.var.shape
        result = dict(shape=(shape[-2], shape[-1]))
        result.update(self.var.attrs)
        result.update(
            dict(
                north=self.north,
                south=self.south,
                east=self.east,
                west=self.west,
                # # TODO:
                # south_north_increment=None,
                # west_east_increment=None,
            )
        )
        return result

    def to_xarray(self):
        return self.data


class XArrayDataArrayWrapper(Wrapper):
    def __init__(self, data):
        self.data = data

    def to_datetime_list(self):
        return to_datetime_list(self.data.values)


def wrapper(data, *args, **kwargs):
    import xarray as xr

    if isinstance(data, xr.Dataset):
        return XArrayDatasetWrapper(data, *args, **kwargs)

    if isinstance(data, xr.DataArray):
        try:
            return XArrayDatasetWrapper(data.to_dataset(), *args, **kwargs)
        except ValueError:
            return XArrayDataArrayWrapper(data, *args, **kwargs)

    return None
