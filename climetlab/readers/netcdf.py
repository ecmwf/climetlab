# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# The code is copied from skinnywms, and we should combile later

import datetime
from contextlib import closing
from itertools import product

import numpy as np
import xarray as xr

from climetlab.utils.bbox import BoundingBox

from . import Reader


def as_datetime(self, time):
    return datetime.datetime.strptime(str(time)[:19], "%Y-%m-%dT%H:%M:%S")


def as_level(self, level):
    n = float(level)
    if int(n) == n:
        return int(n)
    return n


class Slice:
    def __init__(self, name, value, index, is_dimension, is_info):
        self.name = name
        self.index = index
        self.value = value
        self.is_dimension = (not is_info,)
        self.is_info = is_info

    def __repr__(self):
        return "[%s:%s=%s]" % (self.name, self.index, self.value)


class TimeSlice(Slice):
    pass


class Coordinate:
    def __init__(self, variable, info):
        self.variable = variable
        # We only support 1D coordinate for now
        # assert len(variable.dims) == 1
        self.is_info = info
        self.is_dimension = not info

        if variable.values.ndim == 0:
            self.values = [self.convert(variable.values)]
        else:
            self.values = [self.convert(t) for t in variable.values][:10]

    def make_slice(self, value):
        return self.slice_class(
            self.variable.name,
            value,
            self.values.index(value),
            self.is_dimension,
            self.is_info,
        )

    def __repr__(self):
        return "%s[name=%s,values=%s]" % (
            self.__class__.__name__,
            self.variable.name,
            len(self.values),
        )


class TimeCoordinate(Coordinate):
    slice_class = TimeSlice
    is_dimension = True
    convert = as_datetime


class LevelCoordinate(Coordinate):
    # This class is just in case we want to specialise
    # 'level', othewise, it is the same as OtherCoordinate
    slice_class = Slice
    is_dimension = False
    convert = as_level


class OtherCoordinate(Coordinate):
    slice_class = Slice
    is_dimension = False
    convert = as_level


class NetCDFField:
    def __init__(self, path, ds, variable, slices):

        dims = ds[variable].dims

        latitude = ds[variable][dims[-2]]
        longitude = ds[variable][dims[-1]]

        self.north = np.amax(latitude.data)
        self.south = np.amin(latitude.data)
        self.east = np.amax(longitude.data)
        self.west = np.amin(longitude.data)

        self.path = path
        self.variable = variable
        self.slices = slices

        self.name = self.variable

        self.title = getattr(
            ds[self.variable],
            "long_name",
            getattr(ds[self.variable], "standard_name", self.variable),
        )

        self.time = None

        for s in self.slices:

            if isinstance(s, TimeSlice):
                self.time = s.value

            if s.is_info:
                self.title += " (" + s.name + "=" + str(s.value) + ")"

    def plot_map(self, driver):

        dimensions = dict((s.name, s.index) for s in self.slices)

        driver.bounding_box(
            north=self.north, south=self.south, west=self.west, east=self.east
        )

        driver.plot_netcdf(self.path, self.variable, dimensions)

    def __repr__(self):
        return "NetCDFField[%r,%r]" % (self.variable, self.slices)

    def to_datetime_list(self):
        raise NotImplementedError

    def to_bounding_box(self):
        return BoundingBox(
            north=self.north, south=self.south, east=self.east, west=self.west
        )


class NetCDFReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)
        self.fields = None

    def _scan(self):
        if self.fields is None:
            self.fields = self.get_fields()

    def __repr__(self):
        return "NetCDFReader(%s)" % (self.path,)

    def __iter__(self):
        self._scan()
        return iter(self.fields)

    def __len__(self):
        self._scan()
        return len(self.fields)

    def __getitem__(self, n):
        self._scan()
        return self.fields[n]

    def get_fields(self):
        with closing(
            xr.open_mfdataset(self.path, combine="by_coords")
        ) as ds:  # or nested
            return self._get_fields(ds)

    def _get_fields(self, ds):  # noqa C901
        # Select only geographical variables

        fields = []

        skip = set()

        for name in ds.data_vars:
            v = ds[name]
            skip.update(getattr(v, "coordinates", "").split(" "))
            skip.update(getattr(v, "bounds", "").split(" "))

        for name in ds.data_vars:

            if name in skip:
                continue

            v = ds[name]

            coordinates = []

            # self.log.info('Scanning file: %s var=%s coords=%s', self.path, name, v.coords)

            info = [value for value in v.coords if value not in v.dims]

            for coord in v.coords:
                c = ds[coord]

                # self.log.info("COORD %s %s %s %s", coord, type(coord), hasattr(c, 'calendar'), c)

                standard_name = getattr(c, "standard_name", None)
                axis = getattr(c, "axis", None)
                long_name = getattr(c, "long_name", None)

                use = False

                if standard_name in ("longitude", "projection_x_coordinate") or (
                    long_name == "longitude"
                ):
                    has_lon = True
                    use = True

                if standard_name in ("latitude", "projection_y_coordinate") or (
                    long_name == "latitude"
                ):
                    has_lat = True
                    use = True

                # Of course, not every one sets the standard_name
                if standard_name in ("time", "forecast_reference_time") or axis == "T":
                    coordinates.append(TimeCoordinate(c, coord in info))
                    use = True

                # TODO: Support other level types
                if standard_name in (
                    "air_pressure",
                    "model_level_number",
                    "altitude",
                ):  # or axis == 'Z':
                    coordinates.append(LevelCoordinate(c, coord in info))
                    use = True

                if axis in ("X", "Y"):
                    use = True

                if not use:
                    coordinates.append(OtherCoordinate(c, coord in info))

            if not (has_lat and has_lon):
                # self.log.info("NetCDFReader: skip %s (Not a 2 field)", name)
                continue

            for values in product(*[c.values for c in coordinates]):

                slices = []
                for value, coordinate in zip(values, coordinates):
                    slices.append(coordinate.make_slice(value))

                fields.append(NetCDFField(self.path, ds, name, slices))

        if not fields:
            raise Exception("NetCDFReader no 2D fields found in %s" % (self.path,))

        return fields

    def to_xarray(self):
        return xr.open_dataset(self.path)
