# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from datetime import timedelta
from functools import cached_property

import numpy as np

from climetlab.indexing.fieldset import Field
from climetlab.utils.bbox import BoundingBox

from .coords import LevelSlice, TimeSlice
from .dataset import DataSet


class NetCDFField(Field):
    def __init__(self, owner, ds, variable, slices, non_dim_coords):
        data_array = ds[variable]

        self.owner = owner
        self.variable = variable
        self.slices = slices
        self.non_dim_coords = non_dim_coords
        self.shape = (data_array.shape[-2], data_array.shape[-1])
        self.ds = ds

        self.name = self.variable

        self.title = getattr(
            data_array,
            "long_name",
            getattr(data_array, "standard_name", self.variable),
        )

        self.time = non_dim_coords.get("valid_time", non_dim_coords.get("time"))
        self.level = None
        self.levtype = "sfc"

        for s in self.slices:
            if isinstance(s, TimeSlice):
                self.time = s.value

            if s.is_info:
                self.title += " (" + s.name + "=" + str(s.value) + ")"

            if isinstance(s, LevelSlice):
                self.level = s.value
                self.levtype = {"pressure": "pl"}.get(s.name, s.name)

        if "forecast_reference_time" in ds.data_vars:
            forecast_reference_time = ds["forecast_reference_time"].data
            assert forecast_reference_time.ndim == 0, forecast_reference_time
            forecast_reference_time = forecast_reference_time.astype("datetime64[s]")
            forecast_reference_time = forecast_reference_time.astype(object)
            step = (self.time - forecast_reference_time).total_seconds()
            assert step % 3600 == 0, step
            self.step = int(step // 3600)

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
            north=self.north,
            south=self.south,
            east=self.east,
            west=self.west,
        )

    @cached_property
    def grid_mapping(self):
        def tidy(x):
            if isinstance(x, np.ndarray):
                return x.tolist()
            if isinstance(x, (tuple, list)):
                return [tidy(y) for y in x]
            if isinstance(x, dict):
                return {k: tidy(v) for k, v in x.items()}
            return x

        return tidy(
            self.owner.xr_dataset[
                self.owner.xr_dataset[self.variable].grid_mapping
            ].attrs
        )

    # Compatibility to GRIb fields below

    def grid_points(self):
        return DataSet(self.owner.xr_dataset).grid_points(self.variable)

    def to_numpy(self, reshape=True, dtype=None):
        dimensions = dict((s.name, s.index) for s in self.slices)
        values = self.owner.xr_dataset[self.variable].isel(dimensions).values
        if not reshape:
            values = values.flatten()
        if dtype is not None:
            values = values.astype(dtype)
        return values

    # ----------------------------------------------------------------
    def metadata(self, name):
        return getattr(self, f"_metadata_{name}")()

    def _metadata_valid_datetime(self):
        return self.time.isoformat()

    def _metadata_param(self):
        return self.variable

    def _metadata_step(self):
        return self.step

    def _metadata_levelist(self):
        return self.level

    def _metadata_levtype(self):
        return self.levtype

    def _metadata_number(self):
        # TODO: code me
        return None

    def _metadata_date(self):
        date = self.time - timedelta(hours=self.step)
        return int(date.strftime("%Y%m%d"))

    def _metadata_time(self):
        date = self.time - timedelta(hours=self.step)
        return int(date.strftime("%H%M"))

    # ----------------------------------------------------------------
    def as_mars(self):
        return dict(
            param=self._metadata_param(),
            step=self._metadata_step(),
            levelist=self._metadata_levelist(),
            levtype=self._metadata_levtype(),
            number=self._metadata_number(),
            date=self._metadata_date(),
            time=self._metadata_time(),
        )

    @property
    def mars_area(self):
        # TODO: code me
        return [self.north, self.west, self.south, self.east]

    @property
    def mars_grid(self):
        # TODO: code me
        return None

    # ----------------------------------------------------------------
    @property
    def resolution(self):
        # TODO: code me
        return None

    def valid_datetime(self):
        return self.time.isoformat()

    @property
    def north(self):
        return self.ds.bbox(self.variable)[0]

    @property
    def west(self):
        return self.ds.bbox(self.variable)[1]

    @property
    def south(self):
        return self.ds.bbox(self.variable)[2]

    @property
    def east(self):
        return self.ds.bbox(self.variable)[3]
