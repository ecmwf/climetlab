# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import itertools
import logging
import math

LOG = logging.getLogger(__name__)


def coords_to_index(coords, shape):
    a = 0
    n = 1
    i = len(coords) - 1
    while i >= 0:
        a += coords[i] * n
        n *= shape[i]
        i -= 1
    return a


def index_to_coords(index, shape):
    result = [None] * len(shape)
    i = len(shape) - 1

    while i >= 0:
        result[i] = index % shape[i]
        index = index // shape[i]
        i -= 1
    return tuple(result)


class FieldCube:
    def __init__(self, ds, *args, remapping=None, datetime="valid"):
        assert len(ds), f"No data in {ds}"

        assert datetime == "valid"
        self.datetime = datetime

        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]

        names = []
        for a in args:
            if isinstance(a, str):
                names.append(a)
            elif isinstance(a, dict):
                names += list(a.keys())

        self._field_shape = None

        # Sort the source according to there
        # internal_args = reduce(operator.add, [Separator.split(a) for a in args], [])
        self.source = ds.order_by(*args, remapping=remapping)

        # Get a mapping of user names to unique values
        # With possible reduce dimentionality if the user use 'level+parm'

        self.user_coords = ds.unique_values(*names, remapping=remapping)

        print(f"{self.user_coords=}")

        self.user_shape = tuple(len(v) for k, v in self.user_coords.items())

        if math.prod(self.user_shape) != len(self.source):
            raise ValueError(
                f"Shape {self.user_shape} does not match number of fields {len(self.source)}. "
            )

    @property
    def field_shape(self):
        if self._field_shape is None:
            self._field_shape = self.source[0].shape
        return self._field_shape

    @property
    def extended_user_shape(self):
        return self.user_shape + self.field_shape

    def __str__(self):
        content = ", ".join([f"{k}:{len(v)}" for k, v in self.user_coords.items()])
        return f"{self.__class__.__name__}({content} ({len(self.source)} fields))"

    def squeeze(self):
        # TODO: remove an dimensions of one.
        return self

    def __getitem__(self, indexes):
        # Make sure the requested indexes are a list of slices matching the shape

        if isinstance(indexes, int):
            indexes = (indexes,)  # make tuple

        if isinstance(indexes, list):
            indexes = tuple(indexes)

        assert isinstance(indexes, tuple), (type(indexes), indexes)

        indexes = list(indexes)

        if indexes[-1] is Ellipsis:
            indexes.pop()

        while len(indexes) < len(self.user_shape):
            indexes.append(slice(None, None, None))

        # Map the slices to a list of indexes per dimension

        coords = []
        for s, c in zip(indexes, self.user_coords.values()):
            lst = list(range(len(c)))[s]
            if not isinstance(lst, list):
                lst = [lst]
            coords.append(lst)

        # Transform the coordinates to a list of indexes for the underlying dataset
        dataset_indexes = []
        user_shape = self.user_shape
        for x in itertools.product(*coords):
            i = coords_to_index(x, user_shape)
            dataset_indexes.append(i)

        ds = self.source.from_list(dataset_indexes)

        # If we match just one element, we return it
        if all(len(_) == 1 for _ in coords):
            return ds[0]

        # For more than one element, we return a new cube
        return FieldCube(ds, *self.user_coords)  # user_coords=self.user_coords)

    def to_numpy(self, **kwargs):
        return self.source.to_numpy(**kwargs).reshape(*self.extended_user_shape)

    def _names(self, coords, reading_chunks=None, **kwargs):
        if reading_chunks is None:
            reading_chunks = list(coords.keys())
        if isinstance(reading_chunks, (list, tuple)):
            assert all(isinstance(_, str) for _ in reading_chunks)
            reading_chunks = {k: len(coords[k]) for k in reading_chunks}

        for k, requested in reading_chunks.items():
            full_len = len(coords[k])
            assert full_len == requested, "only full chunks supported for now"

        names = list(coords[a] for a, _ in reading_chunks.items())

        return names

    def count(self, reading_chunks=None):
        names = self._names(reading_chunks=reading_chunks, coords=self.user_coords)
        return math.prod(len(lst) for lst in names)

    def iterate_cubelets(self, reading_chunks=None, **kwargs):
        names = self._names(reading_chunks=reading_chunks, coords=self.user_coords)
        indexes = list(range(0, len(lst)) for lst in names)

        return (
            Cubelet(self, i, indexes_names=n)
            for n, i in zip(itertools.product(*names), itertools.product(*indexes))
        )

    def chunking(self, **chunks):
        if not chunks:
            return True  # Let ZARR choose

        lst = list(self.user_shape)
        for i, name in enumerate(self.user_coords):
            lst[i] = chunks.get(name, lst[i])

        return tuple(lst)


class Cubelet:
    def __init__(self, cube, indexes, indexes_names=None):
        self.owner = cube
        assert all(isinstance(_, int) for _ in indexes), indexes
        self.indexes = indexes
        self.index_names = indexes_names

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.indexes},index_names={self.index_names})"
        )

    @property
    def extended_icoords(self):
        return self.indexes

    def to_numpy(self, **kwargs):
        return self.owner[self.indexes].to_numpy(**kwargs)
