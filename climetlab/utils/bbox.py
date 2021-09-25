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
        self.south = max(float(south), -90.0)

        self.is_periodic_west_east = (east - west) == 360
        self.west = _normalize(float(west), -180)  # Or 0?

        if self.is_periodic_west_east:
            self.east = self.west + 360
        else:
            self.east = _normalize(float(east), self.west)

        if self.north < self.south:
            raise ValueError(
                f"Invalid bounding box, north={self.north} < south={self.south}"
            )

        if self.west > self.east:
            raise ValueError(
                f"Invalid bounding box, west={self.west} > east={self.east}"
            )

        if self.east > self.west + 360:
            raise ValueError(
                f"Invalid bounding box, east={self.east} > west={self.west}+360"
            )

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

    @classmethod
    def multi_merge(cls, bboxes):

        north = max(z.north for z in bboxes)
        south = min(z.south for z in bboxes)

        first = bboxes[0]

        origin = first.east % 360
        full = BoundingBox(
            north=north,
            west=first.west,
            south=south,
            east=first.west + 360,
        )

        # Build the list of provided [west, east] intervals

        boundaries = list()
        stacked_intervals = set()  # To keep track of overlapping intervals
        for i, b in enumerate(bboxes):

            if b.east - b.west == 360:
                return full

            west = (b.west - origin) % 360
            east = (b.east - origin) % 360

            if west > east:
                stacked_intervals.add(i)

            boundaries.append((west, True, i))
            boundaries.append((east, False, i))

        boundaries = sorted(boundaries)

        start = 0
        best = -1
        west = 0
        east = 0

        # Find the longest interval *outside* the provided [west, east] intervals
        # It's complement will be the result

        for cursor, entering, interval in boundaries:

            if entering:
                if not stacked_intervals:
                    distance = cursor - start
                    if distance > best:
                        best = distance
                        west = cursor
                        east = start

                    start = None

                stacked_intervals.add(interval)

            else:  # exiting
                stacked_intervals.remove(interval)
                if not stacked_intervals:
                    start = cursor

        if best <= 0:
            return full

        return BoundingBox(
            north=north,
            west=origin + west,
            south=south,
            east=origin + east,
        )

    def merge(self, other):
        return self.multi_merge([self, other])

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
