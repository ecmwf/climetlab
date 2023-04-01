# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import logging

import numpy as np

from climetlab.decorators import cached_method
from climetlab.readers.grib.index import FieldSet
from climetlab.utils.dates import to_datetime

LOG = logging.getLogger(__name__)


class ConstantGenerator:
    def __init__(self, field):
        self.field = field

    @cached_method
    def grid_points(self):
        return self.field.grid_points()

    @cached_method
    def ecef_xyz(self):
        # https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_geodetic_to_ECEF_coordinates
        # We assume that the Earth is a sphere of radius 1 so N(phi) = 1
        # We assume h = 0

        lat, lon = self.grid_points()

        phi = np.deg2rad(lat)
        lda = np.deg2rad(lon)

        cos_phi = np.cos(phi)
        cos_lda = np.cos(lda)
        sin_phi = np.sin(phi)
        sin_lda = np.sin(lda)

        x = cos_phi * cos_lda
        y = cos_phi * sin_lda
        z = sin_phi

        return x, y, z

    def latitudes(self, date):
        return self.grid_points()[0]

    @cached_method
    def cos_latitudes_(self):
        return np.cos(np.deg2rad(self.grid_points()[0]))

    def cos_latitudes(self, date):
        return self.cos_latitudes_()

    @cached_method
    def sin_latitudes_(self):
        return np.sin(np.deg2rad(self.grid_points()[0]))

    def sin_latitudes(self, date):
        return self.sin_latitudes_()

    def longitudes(self, date):
        return self.grid_points()[1]

    @cached_method
    def cos_longitudes_(self):
        return np.cos(np.deg2rad(self.grid_points()[1]))

    def cos_longitudes(self, date):
        return self.cos_longitudes_()

    @cached_method
    def sin_longitudes_(self):
        return np.sin(np.deg2rad(self.grid_points()[1]))

    def sin_longitudes(self, date):
        return self.sin_longitudes_()

    def ecef_x(self, date):
        return self.ecef_xyz()[0]

    def ecef_y(self, date):
        return self.ecef_xyz()[1]

    def ecef_z(self, date):
        return self.ecef_xyz()[2]

    def julian_day(self, date):
        date = to_datetime(date)
        delta = date - datetime.datetime(date.year, 1, 1)
        julian_day = delta.days + delta.seconds / 86400.0
        return np.full(self.field.shape, julian_day)

    def cos_julian_day(self, date):
        radians = self.julian_day(date) / 365.25 * np.pi * 2
        return np.cos(radians)

    def sin_julian_day(self, date):
        radians = self.julian_day(date) / 365.25 * np.pi * 2
        return np.sin(radians)

    def local_time(self, date):
        lon = self.longitudes(date)
        date = to_datetime(date)
        delta = date - datetime.datetime(date.year, date.month, date.day)
        since_midnight = delta.days + delta.seconds / 86400.0
        return (lon / 360 * 24.0 + since_midnight) % 24

    def cos_local_time(self, date):
        radians = self.local_time(date) / 24 * np.pi * 2
        return np.cos(radians)

    def sin_local_time(self, date):
        radians = self.local_time(date) / 24 * np.pi * 2
        return np.sin(radians)


class Constants(FieldSet):
    def __init__(self, data, names):
        self.data = data
        self.names = names
        self.params = data.unique_values("param")["param"]

    def __len__(self):
        return len(self.data) * len(self.names) // len(self.params)

    def _getitem(self, i):
        assert False

    def mutate(self):
        return self


source = Constants
