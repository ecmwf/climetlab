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
from collections import defaultdict

LOG = logging.getLogger(__name__)


class FieldCube:
    def __init__(self, ds, *args, datetime="valid"):
        assert len(ds), f"No data in {ds}"

        assert datetime == "valid"
        self.datetime = datetime

        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = [_ for _ in args[0]]

        self._field_shape = None
        LOG.debug(f"* New FieldCube(args={args})")

        self.source = ds.order_by(*args)

        self.user_coords, self.internal_coords, self.slices = self._build_coords(
            self.source, args
        )

        LOG.debug(f"{self.internal_coords=}")
        LOG.debug(f"{self.user_coords=}")
        LOG.debug("slices=", self.slices)

        self.internal_shape = tuple(len(v) for k, v in self.internal_coords.items())

        self.user_shape = tuple(len(v) for k, v in self.user_coords.items())
        # for s in self.slices:
        #     n = math.prod(self.internal_shape[s])
        #     self.user_shape.append(n)
        # self.user_shape = tuple(self.user_shape)

        print(f"{self.user_shape=}")
        print(f"{self.internal_shape=}")

        self.user_ndim = len(self.user_shape)

        # self.check_shape(self.internal_shape)
        self.check_shape(self.user_shape)
        LOG.debug("extended_shape=", self.extended_user_shape)

    @property
    def field_shape(self):
        if self._field_shape is None:
            self._field_shape = self.source[0].shape
            LOG.debug("fieldshape=", self._field_shape)
        return self._field_shape

    @property
    def extended_user_shape(self):
        return self.user_shape + self.field_shape

    @property
    def extended_internal_shape(self):
        return self.internal_shape + self.field_shape

    def __str__(self):
        content = ", ".join([f"{k}:{len(v)}" for k, v in self.user_coords.items()])
        return f"{self.__class__.__name__}({content} ({len(self.source)} fields))"

    def _transform_args(self, u_args):
        internal_args = []
        slices = []
        splits = []
        i = 0
        for a in u_args:
            lst = a.split("_")
            internal_args += lst
            slices.append(slice(i, i + len(lst)))
            splits.append(tuple(lst))
            i += len(lst)
        return internal_args, slices, splits

    def _build_coords(self, ds, args):
        user_args = args
        internal_args, slices, splits = self._transform_args(args)
        internal_coords = ds.unique_values(*internal_args)

        if all(len(s) == 1 for s in splits):
            return internal_coords, internal_coords, slices

        # We have some splits

        user_coords = defaultdict(dict)

        for p in ds.combinations(*internal_args):
            for name, split in zip(user_args, splits):
                user_coords[name][
                    "_".join(str(p[s]) for s in split if p[s] is not None)
                ] = True

        user_coords = {k: list(user_coords[k].keys()) for k in user_args}  # reordering
        assert math.prod(len(v) for v in user_coords.values()) == len(ds), (
            len(ds),
            user_coords,
        )

        print("user_coords", user_coords)

        return user_coords, internal_coords, slices

    def squeeze(self):
        return self
        # args = [k for k, v in self.coords.items() if len(v) > 1]
        # if not args:
        #     # LOG.warn...
        #     return self
        # return FieldCube(self.source, *args, datetime=self.datetime)

    def check_shape(self, shape):
        print("XXXX shape=", shape)
        if math.prod(shape) != len(self.source):
            msg = f"{shape} -> {math.prod(shape)} requested fields != {len(self.source)} available fields. "
            print("ERROR:", msg)
            raise ValueError(f"{msg}")

    def __getitem__(self, indexes):
        # indexes are user_indexes

        if isinstance(indexes, int):
            indexes = (indexes,)  # make tuple
        if isinstance(indexes, list):
            indexes = tuple(indexes)
        assert isinstance(indexes, tuple), (type(indexes), indexes)

        indexes = list(indexes)

        if indexes[-1] is Ellipsis:
            indexes.pop()

        while len(indexes) < self.user_ndim:
            indexes.append(slice(None, None, None))

        assert len(indexes) == len(self.user_shape), (indexes, self.user_shape)

        u_args = []
        selection_dict = defaultdict(list)

        u_names = self.user_coords.keys()
        assert len(u_names) == len(indexes), (u_names, indexes, self.user_coords)
        for i, u_name in zip(indexes, u_names):
            u_values = self.user_coords[u_name]

            if isinstance(i, int):
                if i >= len(u_values):
                    raise IndexError(f"index {i} out of range in {u_name} = {u_values}")

            if isinstance(i, slice):
                u_args.append(u_name)

            u_list = u_values[i]
            if not isinstance(u_list, (list, tuple)):
                u_list = [u_list]
                assert not isinstance(i, slice)

            if "_" not in u_name:
                selection_dict[u_name] = u_list
            else:
                internal_names = u_name.split("_")
                for u_value in u_list:
                    internal_values = u_value.split("_")
                    assert len(internal_values) == len(internal_names)
                    for n, v in zip(internal_names, internal_values):
                        if v != "None":
                            # TODO: decide for param_level = "2t" or = "2t_None"
                            selection_dict[n].append(v)

        if all(isinstance(x, int) for x in indexes):
            # # optimized version, we could use :
            # np.ravel_multi_index(indexes, self.internal_shape)
            # return self.source[i]
            # non-optimized version:
            _ds = self.source.sel(selection_dict)
            assert len(_ds) == 1, (len(_ds), selection_dict, f"{indexes=}")
            return _ds[0]

        _ds = self.source.sel(selection_dict)
        return FieldCube(_ds, *u_args)

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
        return True
        if not chunks:
            return True

        out = []
        for k, v in self.coords.items():
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

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.indexes},index_names={self.index_names})"
        )

    @property
    def extended_icoords(self):
        return self.indexes

    def to_numpy(self, **kwargs):
        return self.owner[self.indexes].to_numpy(**kwargs)
