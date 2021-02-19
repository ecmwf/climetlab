# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from climetlab.helpers import helper


class BoundingBox:
    def __init__(self, *, north, west, south, east):
        # Convert to float as these values may come from Numpy
        self.north = min(float(north), 90.0)
        self.west = float(west)
        self.south = max(float(south), -90.0)
        self.east = float(east)

        if self.north <= self.south:
            raise ValueError(
                "North (%s) must be greater than south (%s)"
                % (
                    self.north,
                    self.south,
                )
            )

        if self.west == self.east:
            raise ValueError("West (%s) is equal to east (%s)" % (west, east))

        while self.east < self.west:
            self.east += 360

        while self.east - self.west > 360:
            self.east -= 360

        while self.east >= 360 and self.west >= 360:
            self.east -= 360
            self.west -= 360

        while self.east < -180 and self.west < -180:
            self.east += 360
            self.west += 360

    def __repr__(self):
        return "BoundingBox(north=%g,west=%g,south=%g,east=%g)" % (
            self.north,
            self.west,
            self.south,
            self.east,
        )

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return self.as_tuple() == other.as_tuple()

    @property
    def width(self):
        return self.east - self.west

    @property
    def height(self):
        return self.north - self.south

    def merge(self, other):

        west1, east1 = self.west, self.east
        west2, east2 = other.west, other.east

        while west1 < 0 or east1 < 0:
            west1 += 360
            east1 += 360

        while west2 < 0 or east2 < 0:
            west2 += 360
            east2 += 360

        if abs(west1 - (west2 + 360)) < abs(west1 - west2):
            east2, west2 = east2 + 360, west2 + 360
        elif abs(west2 - (west1 + 360)) < abs(west2 - west1):
            east1, west1 = east1 + 360, west1 + 360

        # print(west1, east1, west2, east2)
        return BoundingBox(
            north=max(self.north, other.north),
            west=min(west1, west2),
            south=min(self.south, other.south),
            east=max(east1, east2),
        )

    def add_margins(self, margins):

        if isinstance(margins, str) and margins[-1] == "%":
            margins = int(margins[:-1]) / 100.0
            margins = max(
                (self.north - self.south) * margins, (self.east - self.west) * margins
            )

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

    def as_list(self):
        return [self.north, self.west, self.south, self.east]

    def as_tuple(self):
        return (self.north, self.west, self.south, self.east)

    def as_dict(self):
        return dict(north=self.north, west=self.west, south=self.south, east=self.east)


def to_bounding_box(obj):

    if isinstance(obj, BoundingBox):
        return obj

    if isinstance(obj, (list, tuple)):
        return BoundingBox(north=obj[0], west=obj[1], south=obj[2], east=obj[3])

    if getattr(obj, "to_bounding_box", None) is None:
        obj = helper(obj)

    return to_bounding_box(obj.to_bounding_box())
