# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


class BoundingBox:
    def __init__(self, *, north, west, south, east):
        # Convert to float as these values may come from Numpy
        self.north = min(float(north), 90.0)
        self.west = float(west)
        self.south = max(float(south), -90.0)
        self.east = float(east)

        assert self.north > self.south, "North (%s) must be greater than south (%s)" % (
            self.north,
            self.south,
        )

        assert self.west != self.east

        while self.east - self.west > 360:
            self.east -= 360

    def _repr_(self):
        return "BoundingBox(north=%g,west=%g,south=%g,east=%g)" % (
            self.north,
            self.west,
            self.south,
            self.east,
        )

    def merge(self, other):
        # TODO:check east/west
        return BoundingBox(
            north=max(self.north, other.north),
            west=min(self.west, other.west),
            south=min(self.south, other.south),
            east=max(self.east, other.east),
        )

    def add_margins(self, margins):
        # TODO:check east/west
        margins_lat = margins
        margins_lon = margins

        if self.east - self.west > 360 - 2 * margins:
            margins = (360 - (self.east - self.west)) / 2.0

        return BoundingBox(
            north=self.north + margins_lat,
            west=self.west - margins_lon,
            south=self.south - margins_lat,
            east=self.east + margins_lon,
        )
