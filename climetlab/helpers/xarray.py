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


class XArrayDatasetHelper:
    def __init__(self, data):

        # data.climetlab.foo(42)

        latitude = None
        longitude = None

        for name, var in itertools.chain(data.coords.items(), data.data_vars.items()):
            if var.attrs.get("standard_name") == "latitude":
                assert latitude is None
                latitude = var

            if var.attrs.get("standard_name") == "longitude":
                assert longitude is None
                longitude = var

        self.data = data
        dims = 0
        for name, var in data.data_vars.items():

            if len(var.dims) > dims:
                self.name = name
                self.var = var
                self.extra_dims = var.dims[:-2]
                dims = len(var.dims)

        if latitude is None or longitude is None:
            assert latitude is None and longitude is None

            lat, lon = self.var.dims[-2], self.var.dims[-1]
            latitude = data[lat]
            longitude = data[lon]

            # For Magics
            latitude.attrs["standard_name"] = "latitude"
            longitude.attrs["standard_name"] = "longitude"

        self.north = np.amax(latitude.data)
        self.south = np.amin(latitude.data)
        self.east = np.amax(longitude.data)
        self.west = np.amin(longitude.data)

    def plot_map(self, driver):
        driver.bounding_box(
            north=self.north, south=self.south, west=self.west, east=self.east
        )

        dimension_settings = dict()

        for d in self.extra_dims:
            dimension_settings[d] = 0  # self.data[d].data[0]

        driver.plot_xarray(self.data, self.name, dimension_settings)

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


class XArrayDataArrayHelper:
    def __init__(self, data):
        self.data = data

    def to_datetime_list(self):
        return to_datetime_list(self.data.values)


def helper(data, *args, **kwargs):
    import xarray as xr

    if isinstance(data, xr.Dataset):
        return XArrayDatasetHelper(data, *args, **kwargs)

    if isinstance(data, xr.DataArray):
        try:
            return XArrayDatasetHelper(data.to_dataset(), *args, **kwargs)
        except ValueError:
            return XArrayDataArrayHelper(data, *args, **kwargs)

    return None
