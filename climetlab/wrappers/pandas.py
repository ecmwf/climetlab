# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.wrappers import Wrapper

LATLON = (
    ("lat@hdr", "lon@hdr"),
    ("lat", "lon"),
    ("latitude", "longitude"),
    ("LAT", "LON"),
    ("LATITUDE", "LONGITUDE"),
)


class PandasFrameWrapper(Wrapper):
    def __init__(self, frame, **kwargs):

        self.frame = frame

        self.lat = "cannot-find-latitude-column"
        self.lon = "cannot-find-longitude-column"

        self.time = "time"
        if "time" not in self.frame:
            self.time = "date"

        for lat, lon in LATLON:
            if lat in self.frame:
                self.lat, self.lon = lat, lon
                break

    def plot_graph(self, backend):
        column = backend.option("column", self.time)

        backend.plot_graph_pandas(self.frame, self.time, column)

    def plot_map(self, backend):

        column = backend.option("column", self.lat)

        north, west, south, east = self.bounding_box()

        backend.bounding_box(
            north=north,
            south=south,
            west=west,
            east=east,
        )

        backend.plot_pandas(self.frame, self.lat, self.lon, column)

    def bounding_box(self):

        north = self.frame[self.lat].max()
        south = self.frame[self.lat].min()

        lons1 = self.frame[self.lon]
        east1 = lons1.max()
        west1 = lons1.min()

        lons2 = self.frame[self.lon] % 360
        east2 = lons2.max()
        west2 = lons2.min()

        if abs(east1 - west1) <= abs(east2 - west2):
            east, west = east1, west1
        else:
            east, west = east2, west2

        return [north, west, south, east]

    def to_datetime_list(self):
        return sorted(set(self.frame[self.time].values))

    def to_bounding_box(self):
        return self.bounding_box()


class DatetimeIndexWrapper(Wrapper):
    def __init__(self, index, **kwargs):
        self.index = index

    def to_datetime_list(self):
        return [d.to_pydatetime() for d in self.index]


def wrapper(data, *args, **kwargs):
    import pandas as pd

    if isinstance(data, pd.DatetimeIndex):
        return DatetimeIndexWrapper(data, *args, **kwargs)

    if isinstance(data, pd.DataFrame):
        return PandasFrameWrapper(data, *args, **kwargs)

    return None
