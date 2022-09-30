# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import time

import numpy as np


class Helper:
    def __init__(self):
        self.best = None
        self.max = float("inf")


class KDNode:
    __slots__ = "value", "axis", "left", "right", "payload"

    def __init__(self, value, axis):
        self.value = value[:-1]
        self.payload = value[-1]
        self.axis = axis
        self.left = None
        self.right = None

    def visit(self, visitor, depth):
        visitor(self, depth)
        if self.left:
            self.left.visit(visitor, depth + 1)
        if self.right:
            self.right.visit(visitor, depth + 1)

    def find_nn(self, point):
        o = Helper()
        self._find_nn(point, o, 0)
        return (o.best, o.max)

    def _find_nn(self, point, o, depth):

        x = point[self.axis]
        y = self.value[self.axis]

        if x < y:
            if self.left:
                self.left._find_nn(point, o, depth + 1)
        else:
            if self.right:
                self.right._find_nn(point, o, depth + 1)

        d = np.linalg.norm(point - self.value)
        if d < o.max:
            o.max = d
            o.best = self.payload

        d = np.fabs(x - y)

        if d < o.max:
            # Cross over: Visit other subtree...
            if x < y:
                if self.right:
                    self.right._find_nn(point, o, depth + 1)
            else:
                if self.left:
                    self.left._find_nn(point, o, depth + 1)


class KDChunk:
    __slots__ = "values"

    def __init__(self, values):
        self.values = values

    def visit(self, visitor, depth):
        visitor(self, depth)

    def _find_nn(self, point, o, depth):

        d = min((np.linalg.norm(point - v[:-1]), v[-1]) for v in self.values)

        if d[0] < o.max:
            o.max = d[0]
            o.best = d[1]


class KDTree:
    def __init__(self, dimensions, values, chunk_size=-1):
        self.dimensions = dimensions
        self.chunk_size = chunk_size
        self.root = self.build(values)

    def build(self, values, depth=0):
        if len(values) == 0:
            return None

        if len(values) <= self.chunk_size:
            return KDChunk(values)

        k = self.dimensions
        axis = depth % k
        # print(values.shape, values[0])
        values = values[np.argsort(values[:, axis])]

        median = len(values) // 2

        node = KDNode(values[median], axis)
        node.left = self.build(values[:median], depth + 1)
        node.right = self.build(values[median + 1 :], depth + 1)

        return node

    def find_nn(self, point):
        return self.root.find_nn(point)

    def depth(self):
        class visitor:
            def __init__(self):
                self.depth = 0

            def __call__(self, _, depth):
                if depth > self.depth:
                    self.depth = depth

        v = visitor()
        self.root.visit(v, 0)
        return v.depth + 1

    def size(self):
        class visitor:
            def __init__(self):
                self.size = 0

            def __call__(self, _, depth):
                self.size += 1

        v = visitor()
        self.root.visit(v, 0)
        return v.size


CACHE = {}


def sin_cos(x):
    if x not in CACHE:
        y = np.deg2rad(x)
        CACHE[x] = (np.sin(y), np.cos(y))
    return CACHE[x]


def ecef(lat, lon, i):
    # ECEF (Earth-Centered, Earth-Fixed) coordinate system
    sin_lat, cos_lat = sin_cos(lat)
    sin_lon, cos_lon = sin_cos(lon)

    return np.array(
        [
            cos_lat * cos_lon,
            cos_lat * sin_lon,
            sin_lat,
            i,
        ]
    )


def unstructed_to_structed(grib, chunk_size=-1):

    now = time.time()
    print("----")
    xyz = np.array(
        [ecef(lat, lon, i) for i, (lat, lon) in enumerate(grib.iterate_grid_points())]
    )
    print("----", time.time() - now)
    print(len(xyz))

    now = time.time()
    tree = KDTree(3, xyz, chunk_size)
    print("----", time.time() - now)
    return tree


def lookup(tree, lat, lon):
    xyz = ecef(lat / 10, lon / 10, 0)
    return tree.find_nn(xyz[:-1])[0]
    # print(xyz)
    # print("----", time.time() - now)
    # print(tree.size(), tree.depth())
    # now = time.time()
    # z = []
    # for lat in range(900, -901, -1):
    #     for lon in range(0, 3601):
    #         xyz = ecef(lat / 10, lon / 10, 0)
    #         z.append(tree.find_nn(xyz[:-1])[0])
    # print("----", time.time() - now)
    # print(np.array(z))
    # return time.time() - start
