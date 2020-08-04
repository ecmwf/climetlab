# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#


class Driver:
    def __init__(self, *args, **kwargs):
        pass

    def bounding_box(self, north, west, south, east):
        pass

    def plot_grib(self, path, offset):
        pass

    def plot_netcdf(self, params):
        pass

    def plot_numpy(
        self, data, north, west, south_north_increment, west_east_increment, metadata
    ):
        pass

    def plot_xarray(self, ds, variable, dimension_settings={}):
        pass

    def show(self, *args, **kwargs):
        pass
