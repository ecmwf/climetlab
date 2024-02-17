# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import numpy as np

from climetlab.indexing.fieldset import Field
from climetlab.utils.bbox import BoundingBox

from .coords import LevelSlice, TimeSlice
from .dataset import DataSet


class NetCDFField(Field):
    def __init__(self, owner, ds, variable, slices, non_dim_coords):
        data_array = ds[variable]

        self.north, self.west, self.south, self.east = ds.bbox(variable)

        self.owner = owner
        self.variable = variable
        self.slices = slices
        self.non_dim_coords = non_dim_coords
        self.shape = (data_array.shape[-2], data_array.shape[-1])
        # print("====", self.shape)

        self.name = self.variable
        self._cache = {}

        self.title = getattr(
            data_array,
            "long_name",
            getattr(data_array, "standard_name", self.variable),
        )

        self.time = non_dim_coords.get("valid_time", non_dim_coords.get("time"))
        self.level = None
        # print('====', list(non_dim_coords.keys()))

        for s in self.slices:
            if isinstance(s, TimeSlice):
                self.time = s.value

            if s.is_info:
                self.title += " (" + s.name + "=" + str(s.value) + ")"

            if isinstance(s, LevelSlice):
                self.level = s.value
                # print("LEVEL", s.value, s.index, s.is_info, s.is_dimension)

        if "forecast_reference_time" in ds.data_vars:
            forecast_reference_time = ds["forecast_reference_time"].data
            assert forecast_reference_time.ndim == 0, forecast_reference_time
            forecast_reference_time = forecast_reference_time.astype("datetime64[s]")
            forecast_reference_time = forecast_reference_time.astype(object)
            step = (self.time - forecast_reference_time).total_seconds()
            assert step % 3600 == 0, step
            self.step = step // 3600

    def grid_points(self):
        return DataSet(self.owner.dataset).grid_points(self.variable)

    def to_numpy(self, reshape=True, dtype=None):
        dimensions = dict((s.name, s.index) for s in self.slices)
        values = self.owner.dataset[self.variable].isel(dimensions).values
        if not reshape:
            values = values.flatten()
        if dtype is not None:
            values = values.astype(dtype)
        return values

    def plot_map(self, backend):
        dimensions = dict((s.name, s.index) for s in self.slices)

        backend.bounding_box(
            north=self.north, south=self.south, west=self.west, east=self.east
        )

        backend.plot_netcdf(self.owner.path, self.variable, dimensions)

    def __repr__(self):
        return "NetCDFField[%r,%r]" % (self.variable, self.slices)

    def to_bounding_box(self):
        return BoundingBox(
            north=self.north, south=self.south, east=self.east, west=self.west
        )

    def metadata(self, name):
        if name not in self._cache:
            self._cache[name] = self.owner.flavour.metadata(self, name)
        return self._cache[name]

    @property
    def resolution(self):
        return self.owner.flavour.get_resolution(self)

    def as_mars(self):
        return self.owner.flavour.as_mars(self)

    def valid_datetime(self):
        return self.owner.flavour.get_valid_datetime(self)

    @property
    def mars_area(self):
        return self.owner.flavour.get_area(self)

    @property
    def mars_grid(self):
        return self.owner.flavour.get_grid(self)

    @property
    def levelist(self):
        return self.level

    @property
    def levtype(self):
        # TODO: Support other level types
        return "sfc" if self.level is None else "pl"

    @property
    def projection(self):
        def tidy(x):
            if isinstance(x, np.ndarray):
                return x.tolist()
            if isinstance(x, (tuple, list)):
                return [tidy(y) for y in x]
            if isinstance(x, dict):
                return {k: tidy(v) for k, v in x.items()}
            return x

        return tidy(
            self.owner.dataset[self.owner.dataset[self.variable].grid_mapping].attrs
        )
