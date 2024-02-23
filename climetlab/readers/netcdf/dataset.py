# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import numpy as np


class DataSet:
    """
    Class that wraps a xarray dataset to provide caching
    """

    def __init__(self, ds):
        assert ds is not None
        self._ds = ds
        self._cache = {}

    def __getitem__(self, name):
        return self._ds[name]

    def __getattr__(self, name):
        return getattr(self._ds, name)

    def bbox(self, variable):
        data_array = self[variable]
        dims = data_array.dims

        lat = dims[-2]
        lon = dims[-1]

        key = ("bbox", lat, lon)
        if key in self._cache:
            return self._cache[key]

        lats, lons = self.grid_points(variable)
        north = np.amax(lats)
        west = np.amin(lons)
        south = np.amin(lats)
        east = np.amax(lons)

        self._cache[key] = (north, west, south, east)
        return self._cache[key]

    def grid_points(self, variable):
        data_array = self[variable]
        dims = data_array.dims

        lat = dims[-2]
        lon = dims[-1]

        key = ("grid_points", lat, lon)
        if key in self._cache:
            return self._cache[key]

        if "latitude" in self._ds and "longitude" in self._ds:
            latitude = self._ds["latitude"]
            longitude = self._ds["longitude"]

            if latitude.dims == (lat, lon) and longitude.dims == (lat, lon):
                latitude = latitude.data
                longitude = longitude.data
                return latitude.flatten(), longitude.flatten()

        latitude = data_array[lat]
        longitude = data_array[lon]

        lat, lon = np.meshgrid(latitude.data, longitude.data)

        self._cache[key] = lat.flatten(), lon.flatten()
        return self._cache[key]

    def grid_points_xy(self, variable):
        data_array = self[variable]
        dims = data_array.dims

        lat = dims[-2]
        lon = dims[-1]

        latitude = data_array[lat].data
        longitude = data_array[lon].data

        print(latitude, longitude)

        lat, lon = np.meshgrid(latitude, longitude)

        return lat.flatten(), lon.flatten()
        # return self._cache[key]
