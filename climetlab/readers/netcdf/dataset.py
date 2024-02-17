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
    def __init__(self, ds):
        self._ds = ds
        self._bbox = {}
        self._cache = {}

    @property
    def data_vars(self):
        return self._ds.data_vars

    def __getitem__(self, key):
        if key not in self._cache:
            self._cache[key] = self._ds[key]
        return self._cache[key]

    def bbox(self, variable):
        data_array = self[variable]
        dims = data_array.dims

        lat = dims[-2]
        lon = dims[-1]

        if (lat, lon) not in self._bbox:
            dims = data_array.dims

            latitude = data_array[lat]
            longitude = data_array[lon]

            self._bbox[(lat, lon)] = (
                np.amax(latitude.data),
                np.amin(longitude.data),
                np.amin(latitude.data),
                np.amax(longitude.data),
            )

        return self._bbox[(lat, lon)]

    def grid_points(self, variable):
        data_array = self[variable]
        dims = data_array.dims

        lat = dims[-2]
        lon = dims[-1]

        if "latitude" in self._ds and "longitude" in self._ds:
            latitude = self._ds["latitude"]
            longitude = self._ds["longitude"]

            if latitude.dims == (lat, lon) and longitude.dims == (lat, lon):
                latitude = latitude.data
                longitude = longitude.data
                return latitude.flatten(), longitude.flatten()

            return NotImplemented("Code me")

        latitude = data_array[lat]
        longitude = data_array[lon]

        lat, lon = np.meshgrid(latitude.data, longitude.data)

        return lat.flatten(), lon.flatten()
