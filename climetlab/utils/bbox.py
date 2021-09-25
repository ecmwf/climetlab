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


ORIGIN_MINUS_180 = object()
ORIGIN_0 = object()


class BoundingBox:
    def __init__(self, *, north, west, south, east):
        self.globe = (east - west) == 360
        # Convert to float as these values may come from Numpy
        self._north = min(float(north), 90.0)
        self._south = max(float(south), -90.0)

        assert self.north == self._north
        assert self.south == self._south

        self._east = _normalize(float(east), 0)
        self._west = _normalize(float(west), 0)
        self._convention = ORIGIN_MINUS_180

        if self.north < self.south:
            raise ValueError(
                f"Invalid bounding box, north={self.north} <= south={self.south}"
            )

        if self.west > self.east:
            raise ValueError(
                f"Invalid bounding box, west={self.west} >= east={self.east}"
            )

        if self.east > self.west + 360:
            raise ValueError(
                f"Invalid bounding box, east={self.east} >= west={self.west}+360"
            )

    @property
    def west(self):
        return _normalize(float(self._west), -180)  # Or 0?

    @property
    def east(self):
        if self.globe:
            return self.west + 360
        return _normalize(float(self._east), self.west)

    @property
    def north(self):
        return self._north

    @property
    def south(self):
        return self._south

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

    @classmethod
    def multi_merge(cls, bboxes):

        origin = bboxes[0].east % 360
        full = BoundingBox(
            north=max(z.north for z in bboxes),
            west=bboxes[0].west,
            south=min(z.south for z in bboxes),
            east=bboxes[0].west + 360,
        )

        print("- origin ", origin)

        print("- Bbox")
        for b in bboxes:
            print("  ", b.west, b.east)

        print("- Building boundaries")
        boundaries = list()
        layers = set()
        for i, b in enumerate(bboxes):

            if b.east - b.west == 360:
                return full

            west = (b.west - origin) % 360
            east = (b.east - origin) % 360
            print("  ", b.west, b.east, "->", west, east)

            if west > east:
                layers.add(i)

            boundaries.append((west, 1, i))
            boundaries.append((east, -1, i))

        boundaries = sorted(boundaries)

        print("- Boundaries")
        for b in boundaries:
            print(b)

        start = 0.0
        found = (-1.0, 0.0, 0.0)

        for b in boundaries:

            cursor = b[0]

            print("@cursor=", cursor, layers)

            if b[1] == 1:  # entering
                print(f" entering {b[2]}", cursor, layers)
                if len(list(layers)) == 0:
                    print("  found candidate", (cursor - start, start, cursor))
                    if cursor - start > found[0]:
                        found = (cursor - start, start, cursor)

                    start = None

                layers.add(b[2])

            elif b[1] == -1:  # exiting

                print(f" exiting {b[2]}", cursor, layers)

                layers.remove(b[2])

                if len(list(layers)) == 0:
                    print("  start=", start)
                    start = cursor

            else:
                raise Exception()

        if found[0] == -1:
            return full

        return BoundingBox(
            north=max(z.north for z in bboxes),
            west=origin + found[2],
            south=min(z.south for z in bboxes),
            east=origin + found[1],
        )

    def merge(self, other):
        return self.multi_merge([self, other])

        north1, west1, south1, east1 = self.as_tuple()
        north2, west2, south2, east2 = other.as_tuple()

        if self.is_periodic_west_east:
            return BoundingBox(
                north=max(north1, north2),
                west=west1,
                south=min(south1, south2),
                east=east1,
            )

        if other.is_periodic_west_east:
            return BoundingBox(
                north=max(north1, north2),
                west=west2,
                south=min(south1, south2),
                east=east2,
            )

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
