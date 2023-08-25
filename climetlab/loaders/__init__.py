# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import datetime
import json
import logging
import math
import os
import time
import warnings

import numpy as np

import climetlab as cml
from climetlab.core.order import build_remapping  # noqa:F401
from climetlab.utils import progress_bar
from climetlab.utils.config import LoadersConfig
from climetlab.utils.humanize import bytes, seconds

LOG = logging.getLogger(__name__)


def _tidy(o):
    if isinstance(o, dict):
        return {k: _tidy(v) for k, v in o.items()}

    if isinstance(o, (list, tuple)):
        return [_tidy(v) for v in o]

    if o in (None, True, False):
        return o

    if isinstance(o, (str, int, float)):
        return o

    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

    return str(o)


class FastWriter:
    def __init__(self, array, shape):
        self.array = array
        self.shape = shape

    def stats(self, axis):
        sel = [slice(None)] * len(self.shape)
        sums = np.zeros(self.shape[axis])
        squares = np.zeros(self.shape[axis])
        minima = np.zeros(self.shape[axis])
        maxima = np.zeros(self.shape[axis])
        count = None
        for k in range(self.shape[axis]):
            sel[axis] = k
            values = self.__getitem__(tuple(sel))
            sums[k] = np.sum(values)
            squares[k] = np.sum(values * values)
            minima[k] = np.amin(values)
            maxima[k] = np.amax(values)
            if count is None:
                count = values.size
            else:
                assert count == values.size

        return (count, sums, squares, minima, maxima)


class FastWriterWithoutCache(FastWriter):
    def __setitem__(self, key, value):
        self.array[key] = value

    def __getitem__(self, key):
        return self.array[key]

    def flush(self):
        pass


class FastWriterWithCache(FastWriter):
    def __init__(self, array, shape):
        super().__init__(array, shape)
        self.cache = np.zeros(shape)

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __getitem__(self, key):
        return self.cache[key]

    def flush(self):
        self.array[:] = self.cache[:]


class OffsetView:
    def __init__(self, array, offset, axis, shape):
        self.array = array
        self.offset = offset
        self.axis = axis
        self.shape = shape

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            assert key.start is None and key.stop is None, key
            new_key = tuple(
                slice(self.offset, self.offset + value.shape[i])
                if i == self.axis
                else slice(None)
                for i in range(len(self.shape))
            )
        else:
            new_key = tuple(
                k + self.offset if i == self.axis else k for i, k in enumerate(key)
            )
        self.array[new_key] = value


class LoopItemsFilter:
    def __init__(self, *, loader, parts, **kwargs):
        self.loader = loader

        print("parts", parts)
        if parts is None:
            self.parts = None
            return

        if len(parts) == 1 and "/" in parts[0]:
            total = self.loader.nloops
            i_chunk, n_chunks = parts[0].split("/")
            i_chunk, n_chunks = int(i_chunk), int(n_chunks)
            chunk_size = math.ceil(total / n_chunks)
            parts = range((i_chunk - 1) * chunk_size + 1, i_chunk * chunk_size + 1)

        parts = [int(_) for _ in parts]
        print("parts", parts)

        self.parts = parts

    def __call__(self, iloop, vars):
        if self.parts is None:
            return True
        # iloop index starts at 0
        # self.parts is a list of indices starting at 1
        return (iloop + 1) in self.parts


class Loader:
    def __init__(self, *, path, config, print=print, **kwargs):
        self.main_config = LoadersConfig(config)
        self.path = path
        self.kwargs = kwargs
        self.print = print

    def load(self):
        kwargs = self.kwargs
        print_ = kwargs["print"]

        if "loop" not in self.main_config or self.main_config.loop is None:
            self.load_part(self.main_config, iloop=0, **kwargs)
            return

        #        n = 0
        #        for iloop, vars in enumerate(self.main_config._iter_loops()):
        #            n +=

        self.nloops = self.main_config._len_of_iter_loops()
        filter = LoopItemsFilter(loader=self, **kwargs)
        for iloop, vars in enumerate(self.main_config._iter_loops()):
            print(f"{iloop=}")
            if not filter(iloop, vars):
                print(f" . skipping {iloop=}")
                continue
            part_config = self.main_config.substitute(vars)
            print("------------------------------------------------")
            print(f"Processing : {vars}")
            print_(f"Loading input {iloop+1}/{self.nloops}")
            self.load_part(part_config, iloop=iloop, **kwargs)
            print_(f"Loaded input {iloop+1}/{self.nloops}")

    def load_part(self, config, *, iloop, print_=print, **kwargs):
        cube, grid_points = self.config_to_data_cube(config)

        if iloop == 0:
            array = self.create_array(config, cube, grid_points)
        else:
            array = self.append_array(config, cube, grid_points)

        start = time.time()
        load = 0
        save = 0

        reading_chunks = None
        total = cube.count(reading_chunks)
        for i, cubelet in enumerate(
            progress_bar(
                iterable=cube.iterate_cubelets(reading_chunks),
                total=total,
            )
        ):
            now = time.time()
            data = cubelet.to_numpy()
            load += time.time() - now

            # print("data", data.shape,cubelet.extended_icoords)

            now = time.time()
            array[cubelet.extended_icoords] = data
            save += time.time() - now

            if print_ != print:
                print_(f"{i}/{total}")

        now = time.time()
        self.close()
        save += time.time() - now

        print()
        self.print_info()
        print()

        print(
            f"Elapsed: {seconds(time.time() - start)},"
            f" load time: {seconds(load)},"
            f" write time: {seconds(save)}."
        )
        self._built_flags.set(iloop)


VERSION = 2


def add_zarr_dataset(name, nparray, *, zarr_root, dtype=np.float32):
    if isinstance(nparray, (tuple, list)):
        nparray = np.array(nparray, dtype=dtype)
    a = zarr_root.create_dataset(
        name,
        shape=nparray.shape,
        dtype=dtype,
        overwrite=True,
    )
    a[...] = nparray[...]
    return a


class ZarrBuiltRegistry:
    name = "_built"
    lengths = None
    flags = None
    z = None

    def __init__(self, path):
        assert isinstance(path, str), path
        self.zarr_path = path

    @property
    def total(self):
        return sum(self.lengths)

    @property
    def nlenghts(self):
        return len(self.lengths)

    def create(self, lengths):
        import zarr

        z = zarr.open(self.zarr_path, mode="r+")

        add_zarr_dataset(
            f"{self.name}_lengths",
            lengths,
            zarr_root=z,
            dtype="i4",
            # overwrite=True,
        )
        add_zarr_dataset(
            f"{self.name}_flags",
            len(lengths) * [False],
            zarr_root=z,
            dtype=bool,
            # overwrite=True,
        )

    def set_value(self, i, value):
        import zarr

        assert i < self.size, i
        z = zarr.open(self.zarr_path, mode="w+")
        a = z[self.name]
        a[i] = value

    def set(self, i):
        self.set_value(i, True)

    def unset(self, i):
        self.set_value(i, False)

    def get(self, i=None):
        import zarr

        z = zarr.open(self.zarr_path, mode="r")
        a = z[self.name]
        if i is None:
            return a
        return a[i]


class ZarrLoader(Loader):
    writer = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.z = None
        self.statistics = []

    @property
    def _built_flags(self):
        return ZarrFlagArray("_build", self.path, size=self.nloops)

    @classmethod
    def from_config(cls, *, config, path, **kwargs):
        # config is the path to the config file
        # or a dict with the config
        obj = cls(config=config, path=path, **kwargs)
        return obj

    @classmethod
    def from_path(cls, *, config, path, **kwargs):
        import zarr

        assert os.path.exists(path), path
        z = zarr.open(path, mode="r")
        metadata = z.attrs["climetlab"]
        config = metadata["create_yaml_config"]
        return cls.from_config(config, path=path, **kwargs)

    def iter_loops(self):
        if "loop" not in self.main_config or self.main_config.loop is None:
            raise NotImplementedError()
            yield None  # ?
            return

        for vars in self.main_config._iter_loops():
            yield vars

    def initialise(self):
        """Create empty zarr from self.main_config and self.path"""
        import zarr

        def squeeze_dict(dic):
            keys = list(dic.keys())
            assert len(dic) == 1, keys
            return dic[keys[0]]

        def compute_lengths():
            lengths = []
            for i, vars in enumerate(self.iter_loops()):
                lst = squeeze_dict(vars)
                assert isinstance(lst, (tuple, list)), lst
                lengths.append(len(lst))
            return lengths

        lengths = compute_lengths()
        total_length = sum(lengths)

        def get_one_element_config():
            for i, vars in enumerate(self.iter_loops()):
                keys = list(vars.keys())
                assert len(vars) == 1, keys
                key = keys[0]
                vars = {key: vars[key][0]}
                return self.main_config.substitute(vars)

        config = get_one_element_config()

        cube, grid_points = self.config_to_data_cube(config)

        shape = list(cube.extended_user_shape)
        # Notice that shape[0] can be >1, we replace it be the full length
        shape[0] = total_length
        chunks = cube.chunking(self.main_config.output.chunking)
        dtype = self.main_config.output.dtype

        print(f"Creating ZARR '{self.path}', with {shape=}, " f"{chunks=} and {dtype=}")
        self.z = zarr.open(self.path, mode="w")
        # self._built_flags.create()
        self.z.create_dataset("data", shape=shape, chunks=chunks, dtype=dtype)

        lat = self._add_dataset("latitude", grid_points[0])
        lon = self._add_dataset("longitude", grid_points[1])
        assert lat.shape == lon.shape

        metadata = {}
        metadata["name_to_index"] = self.main_config.output.order_by[
            self.main_config.output.statistics
        ]
        metadata["create_yaml_config"] = _tidy(self.main_config)
        for k, v in self.main_config.get("metadata", {}).items():
            self.z.attrs[k] = v
        self.z.attrs["climetlab"] = metadata
        self.z["data"].attrs["climetlab"] = metadata
        self.z.attrs["version"] = VERSION
        self.z = None

        registry = ZarrBuiltRegistry(self.path)
        registry.create(lengths=lengths)

    def config_to_data_cube(self, config):
        start = time.time()
        data = cml.load_source("loader", config.input)
        assert len(data), f"No data for {config}"
        self.print(f"Done in {seconds(time.time()-start)}, length: {len(data):,}.")

        start = time.time()
        self.print("Sort dataset")
        cube = data.cube(
            config.output.order_by,
            remapping=config.output.remapping,
            flatten_values=config.output.flatten_values,
        )
        cube = cube.squeeze()
        self.print(f"Done in {seconds(time.time()-start)}.")

        grid_points = data[0].grid_points()

        self.print(f"{grid_points=}")
        for i in grid_points:
            self.print(len(i))

        return cube, grid_points

    def append_array(self, config, cube, grid_points):
        import zarr

        self.config = config

        shape = cube.extended_user_shape
        chunks = cube.chunking(config.output.chunking)

        print(f"Appending to ZARR '{self.path}', with {shape=}, " f"{chunks=}")

        self.z = zarr.open(self.path, mode="r+")
        self.zdata = self.z["data"]

        original_shape = self.zdata.shape
        assert len(shape) == len(original_shape)

        axis = config.output.append_axis

        new_shape = []
        for i, (o, s) in enumerate(zip(original_shape, shape)):
            if i == axis:
                new_shape.append(o + s)
            else:
                assert o == s, (original_shape, shape, i)
                new_shape.append(o)

        self.zdata.resize(tuple(new_shape))

        self.writer = FastWriterWithCache(
            OffsetView(
                self.zdata,
                original_shape[axis],
                axis,
                shape,
            ),
            shape,
        )

        return self.writer

    def _add_dataset(self, *args, **kwargs):
        return add_zarr_dataset(*args, **kwargs, zarr_root=self.z)

    def close(self):
        if self.writer is None:
            warnings.warn("FastWriter already closed")
        else:
            self.writer.flush()
            self.statistics.append(self.writer.stats(self.config.statistics_axis))

            self.writer = None

    def print_info(self):
        print(self.z.info)
        print(self.zdata.info)

    @classmethod
    def add_statistics(cls, path, print):
        import zarr

        z = zarr.open(path, mode="r+")
        data = z.data
        shape = z.data.shape
        assert len(shape) in [3, 4]  # if 4, we expect to have latitude/longitude

        stats_shape = (shape[0], shape[1])

        # mean = np.zeros(shape=stats_shape)
        # stdev = np.zeros(shape=stats_shape)
        minimum = np.zeros(shape=stats_shape)
        maximum = np.zeros(shape=stats_shape)
        sums = np.zeros(shape=stats_shape)
        squares = np.zeros(shape=stats_shape)

        for i in range(shape[0]):
            chunk = data[i, ...]
            for j in range(shape[1]):
                values = chunk[j, :]
                minimum[i, j] = np.amin(values)
                maximum[i, j] = np.amax(values)
                sums[i, j] = np.sum(values)
                squares[i, j] = np.sum(values * values)
                # mean[i, j] = sums[i, j] / count[i, j]
                # stdev[i, j] = np.sqrt(
                #     squares[i, j] / count[i, j] - mean[i, j] * mean[i, j]
                # )

        _count = z.data.size / shape[1]
        assert _count == int(_count), _count

        # cls._add_dataset_("mean_by_datetime", mean, zarr_root=z)
        # cls._add_dataset_("stdev_by_datetime", stdev, zarr_root=z)
        # cls._add_dataset_("minimum_by_datetime", minimum, zarr_root=z)
        # cls._add_dataset_("maximum_by_datetime", maximum, zarr_root=z)
        # cls._add_dataset_("sums_by_datetime", sums, zarr_root=z)
        # cls._add_dataset_("squares_by_datetime", squares, zarr_root=z)
        # cls._add_dataset_("count_by_datetime", mean * 0 + count, zarr_root=z)

        _minimum = np.amin(minimum, axis=0)
        _maximum = np.amax(maximum, axis=0)
        _sums = np.sum(sums, axis=0)
        _squares = np.sum(squares, axis=0)
        _mean = _sums / _count
        _stdev = np.sqrt(_squares / _count - _mean * _mean)

        cls._add_dataset_("mean", _mean, zarr_root=z)
        cls._add_dataset_("stdev", _stdev, zarr_root=z)
        cls._add_dataset_("minimum", _minimum, zarr_root=z)
        cls._add_dataset_("maximum", _maximum, zarr_root=z)
        cls._add_dataset_("sums", _sums, zarr_root=z)
        cls._add_dataset_("squares", _squares, zarr_root=z)
        cls._add_dataset_("count", _count, zarr_root=z)


class HDF5Loader:
    def append_array(self, *args, **kwargs):
        raise NotImplementedError("Appending do HDF5 not yet implemented")

    def create_array(
        self,
        dataset,
        shape,
        chunks,
        dtype,
        metadata,
        grid_points,
        nloops,
    ):
        import h5py

        if not isinstance(chunks, tuple):
            chunks = None

        print(
            f"Creating HDD5 file '{self.path}', with {dataset=}, {shape=}, {chunks=} and {dtype=}"
        )

        self.h5 = h5py.File(self.path, mode="w")
        array = self.h5.create_dataset(
            dataset,
            chunks=chunks,
            maxshape=shape,
            dtype=dtype,
            data=np.empty(
                shape
            )  # Can we avoid that? Looks like its needed for chuncking
            # data = h5py.Empty(dtype),
        )
        array.attrs["climetlab"] = json.dumps(_tidy(metadata))
        return array

    def close(self):
        self.h5.close()
        del self.h5

    def print_info(self):
        import h5py

        def h5_tree(h5, depth=0):
            for k, v in h5.items():
                if isinstance(v, h5py._hl.group.Group):
                    h5_tree(v, depth + 1)
                else:
                    print(" " * (depth * 3), k, v)
                    for p, q in v.attrs.items():
                        print(" " * (depth * 3 + 3), p, q)

        size = os.path.getsize(self.path)
        print(f"HDF5 file {self.path}: {size:,} ({bytes(size)})")
        with h5py.File(self.path, mode="r") as f:
            print("Content:")
            h5_tree(f, 1)
