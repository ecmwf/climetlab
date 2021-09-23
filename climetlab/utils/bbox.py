# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from climetlab.wrappers import get_wrapper


def _normalize(lon, minimum):
    while lon < minimum:
        lon += 360

    while lon >= minimum + 360:
        lon -= 360

    return lon


class BoundingBox:
    def __init__(self, *, north, west, south, east):
        # Convert to float as these values may come from Numpy
        self.north = min(float(north), 90.0)
        self.west = _normalize(float(west), -180)  # Or 0?
        self.south = max(float(south), -90.0)
        self.east = _normalize(float(east), self.west)

        if self.north <= self.south:
            raise ValueError(
                f"Invalid bounding box, north={self.north} <= south={self.south}"
            )

        if self.west >= self.east:
            raise ValueError(
                f"Invalid bounding box, west={self.west} >= east={self.east}"
            )

        if self.east >= self.west + 360:
            raise ValueError(
                f"Invalid bounding box, east={self.east} >= west={self.west}+360"
            )

    def __repr__(self):
        return "BoundingBox(north=%g,west=%g,south=%g,east=%g)" % (
            self.north,
            self.west,
            self.south,
            self.east,
        )

    @property
    def is_periodic_west_east(self):
        return (self.west != self.east) and (
            self.west == _normalize(self.east, self.west)
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

        north1, west1, south1, east1 = self.as_tuple()
        north2, west2, south2, east2 = other.as_tuple()

        if abs(west1 - (west2 + 360)) < abs(west1 - west2):
            east2, west2 = east2 + 360, west2 + 360
        elif abs(west2 - (west1 + 360)) < abs(west2 - west1):
            east1, west1 = east1 + 360, west1 + 360

        return BoundingBox(
            north=max(north1, north2),
            west=min(west1, west2),
            south=min(south1, south2),
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

    obj = get_wrapper(obj)

    return to_bounding_box(obj.to_bounding_box())
