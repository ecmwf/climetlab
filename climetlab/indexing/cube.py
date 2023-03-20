# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import itertools
import math
import numpy as np
import logging

LOG = logging.getLogger(__name__)

# class Cube:
#     def __init__(self, ds, *args, **kwargs):
#         assert args[-1] == "lon"
#         assert args[-2] == "lat"
#         args = args[:-2]
#         self._shape_spatial = ds[0].shape
#         self.field_cube = FieldCube(ds, *args, **kwargs)
#         self.shape = self.field_cube.shape + self._shape_spatial
#
#     def __getitem__(self, indexes):
#         item = self.field_cube[indexes[:-2]]
#         return item.to_numpy()[indexes[-2:]]
#
#     def to_numpy(self):
#         return self.ds.to_numpy(**kwargs).reshape(self.shape)


class FieldCube:
    def __init__(self, ds, *args, datetime='valid'):
        assert datetime == 'valid'
        self.datetime = datetime

        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = [_ for _ in args[0]]

        self._field_shape = None
        print(f"* New FieldCube(args={args})")

        self.source = ds.order_by(*args)

        self.coords = self._build_coords(self.source, args)

        self.ndim = len(self.coords)
        self.shape = tuple(len(v) for k, v in self.coords.items())
        self.check_shape()
        print("extended_shape=", self.extended_shape)

    @property
    def field_shape(self):
        if self._field_shape is None:
            self._field_shape = self.source[0].shape
            print("fieldshape=", self._field_shape)
        return self._field_shape

    @property
    def extended_shape(self):
        return self.shape + self.field_shape

    def __str__(self):
        content = ", ".join([f"{k}:{len(v)}" for k, v in self.coords.items()])
        return f"{self.__class__.__name__}({content} ({len(self.source)} fields))"

    def _build_coords(self, ds, args):
        # return a dict where the keys are from the args, in the right order
        # and the values are the coordinate.
        coords = ds._all_coords(args)
        # print(f"finding coords (in {len(self.source)} source={self.source})")
        # print(f"source coords: {list(source_coords.keys())}")
        # print(f"requested coords: {args}")
        from functools import reduce
        import operator
        assert reduce(operator.mul, [len(v) for v in coords.values()], 1) == len(ds)

        coords = {k: coords[k] for k in args}  # reordering

        print(f"-> Coords: {coords}")
        return coords

    def squeeze(self):
        args = [k for k,v in self.coords.items() if len(v)>1]
        return FieldCube(self.source, *args, datetime=self.datetime)

    def check_shape(self):
        print("shape=", self.shape)
        if math.prod(self.shape) != len(self.source):
            msg = f"{self.shape} -> {math.prod(self.shape)} requested fields != {len(self.source)} available fields. "
            print("ERROR:", msg)
            raise ValueError(f"{msg}\n{self.source.availability}")

    def __getitem__(self, indexes):
        if isinstance(indexes, int):
            indexes = [indexes]

        if not isinstance(indexes, tuple):
            indexes = (indexes,)  # make tuple

        indexes = list(indexes)

        if indexes[-1] is Ellipsis:
            indexes.pop()

        while len(indexes) < self.ndim:
            indexes.append(slice(None, None, None))

        assert len(indexes) == len(self.shape), (indexes, self.shape)

        args = []
        selection_dict = {}

        names = self.coords.keys()
        assert len(names) == len(indexes), (names, indexes, self.coords)
        for i, name in zip(indexes, names):
            values = self.coords[name]
            if isinstance(i, int):
                if i >= len(values):
                    raise IndexError(f"index {i} out of range in {name} = {values}")
            selection_dict[name] = values[i]
            if isinstance(i, slice):
                args.append(name)

        if all(isinstance(x, int) for x in indexes):
            # # optimized version:
            # i = np.ravel_multi_index(indexes, self.shape)
            # return self.source[i]
            # non-optimized version:
            _ds = self.source.sel(selection_dict)
            return _ds[0]

        _ds = self.source.sel(selection_dict)
        return FieldCube(_ds, *args)

    def to_numpy(self, **kwargs):
        return self.source.to_numpy(**kwargs).reshape(*self.shape, *self.field_shape)

    def iterate_cubelets(self, reading_chunks=None, **kwargs):
        if reading_chunks is None:
            reading_chunks = list(self.coords.keys())
        if isinstance(reading_chunks, (list, tuple)):
            assert all(isinstance(_, str) for _ in reading_chunks)
            reading_chunks = {k:len(self.coords[k]) for k in reading_chunks}

        for k, requested in reading_chunks.items():
            full_len = len(self.coords[k])
            assert full_len == requested, "only full chunks supported for now"

        names = list(self.coords[a] for a,_ in reading_chunks.items())
        indexes = list(range(0,len(lst)) for lst in names)

        # print('names:',names)
        # print('indexes:',indexes)
        return (Cubelet(self, i, indexes_names=n) for n, i in zip(itertools.product(*names), itertools.product(*indexes)))

    def chunking(self, **chunks):
        if not chunks:
            return True

        out = []
        for k,v in self.coords.items():
            if k in chunks:
                out.append(chunks[k])
            else:
                out.append(len(v))
        out += list(self.field_shape)
        return out


class Cubelet:
    def __init__(self, cube, indexes, indexes_names=None):
        self.owner = cube
        assert all(isinstance(_, int) for _ in indexes), indexes
        self.indexes = indexes
        self.index_names = indexes_names


    def __str__(self):
        return (
            f"{self.__class__.__name__}({self.indexes}, index_names={self.index_names})"
        )

    @property
    def extended_icoords(self):
        # ???
        return self.indexes

    def to_numpy(self, **kwargs):
        return self.owner[self.indexes].to_numpy(**kwargs)