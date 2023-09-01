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
import os
import time
import warnings

import numpy as np
import yaml

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
    def __init__(self, large_array, *, offset, axis, shape):
        """
        A view on a portion of the large_array.
        'axis' is the axis along which the offset applies.
        'shape' is the shape of the view.
        """
        self.large_array = large_array
        self.offset = offset
        self.axis = axis
        self.shape = shape

    def __setitem__(self, key, values):
        if isinstance(key, slice):
            # Ensure that the slice covers the entire view along the axis.
            assert key.start is None and key.stop is None, key

            # Create a new key for indexing the large array.
            new_key = tuple(
                slice(self.offset, self.offset + values.shape[i])
                if i == self.axis
                else slice(None)
                for i in range(len(self.shape))
            )
        else:
            # For non-slice keys, adjust the key based on the offset and axis.
            new_key = tuple(
                k + self.offset if i == self.axis else k for i, k in enumerate(key)
            )
        self.large_array[new_key] = values


class LoopItemsFilter:
    def __init__(self, *, loader, parts, **kwargs):
        self.loader = loader

        if parts is None:
            self.parts = None
            return

        if len(parts) == 1:
            part = parts[0]
            if part.lower() in ["all", "*"]:
                self.parts = None
                return

            if "/" in part:
                i_chunk, n_chunks = part.split("/")
                i_chunk, n_chunks = int(i_chunk), int(n_chunks)

                total = len(self.loader.registry.get_flags())
                assert i_chunk > 0, f"Chunk number {i_chunk} must be positive."
                assert (
                    i_chunk <= total
                ), f"Chunk number {i_chunk} must be less than {total}+1."

                chunk_size = total / n_chunks
                parts = [
                    x
                    for x in range(total)
                    if x >= (i_chunk - 1) * chunk_size and x < i_chunk * chunk_size
                ]

        parts = [int(_) for _ in parts]
        print(f"Running parts: {parts}")

        self.parts = parts

    def __call__(self, iloop, vars):
        if self.parts is None:
            return True
        # iloop index starts at 0
        # self.parts is a list of indices starting at 1
        return iloop in self.parts


class Loader:
    def __init__(self, *, path, config, print=print, **kwargs):
        self.main_config = LoadersConfig(config)
        self.path = path
        self.kwargs = kwargs
        self.print = print
        self.registry = ZarrBuiltRegistry(self.path)

    def load(self, **kwargs):
        import zarr

        self.z = zarr.open(self.path, mode="r+")

        filter = LoopItemsFilter(loader=self, **kwargs)
        nloop = len(list((self.iter_loops())))
        for iloop, vars in enumerate(self.iter_loops()):
            if not filter(iloop, vars):
                continue
            if self.registry.get_flag(iloop):
                print(f" -> Skipping {iloop} total={nloop} (already done)")
                continue
            self.print(f" -> Processing i={iloop=} total={nloop}")

            config = self.main_config.substitute(vars)
            cube = self.config_to_data_cube(config)

            shape = cube.extended_user_shape
            chunks = cube.chunking(config.output.chunking)
            axis = config.output.append_axis

            slice = self.registry.get_slice_for(iloop)
            print(f"Building to ZARR '{self.path}':")
            self.print(f"Building to ZARR at {slice}, with {shape=}, {chunks=}")

            offset = slice.start
            array = FastWriterWithCache(
                OffsetView(self.z["data"], offset=offset, axis=axis, shape=shape),
                shape,
            )

            self.load_datacube(cube, array)

            self.registry.set_flag(iloop)

    def load_datacube(self, cube, array):
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

            # self.print("data", data.shape,cubelet.extended_icoords)

            now = time.time()
            array[cubelet.extended_icoords] = data
            save += time.time() - now

            # if self.print != print:
            #    self.print(f"Read {i+1}/{total}")

        now = time.time()
        array.flush()
        save += time.time() - now

        print("Written")
        self.print_info()
        print("Written.")

        self.print(
            f"Elapsed: {seconds(time.time() - start)},"
            f" load time: {seconds(load)},"
            f" write time: {seconds(save)}."
        )


VERSION = 3


def add_zarr_dataset(name, nparray, *, zarr_root, overwrite=True, dtype=np.float32):
    if isinstance(nparray, (tuple, list)):
        nparray = np.array(nparray, dtype=dtype)
    a = zarr_root.create_dataset(
        name,
        shape=nparray.shape,
        dtype=dtype,
        overwrite=overwrite,
    )
    a[...] = nparray[...]
    return a


class ZarrBuiltRegistry:
    name_lengths = "_build_lengths"
    name_flags = "_build_flags"
    lengths = None
    flags = None
    z = None

    def __init__(self, path):
        assert isinstance(path, str), path
        self.zarr_path = path

    def get_slice_for(self, iloop):
        lengths = self.get_lengths()
        assert iloop >= 0 and iloop < len(lengths)
        start = sum(lengths[:iloop])
        stop = sum(lengths[: (iloop + 1)])
        return slice(start, stop)

    def get_lengths(self):
        z = self._open_read()
        return list(z[self.name_lengths][:])

    def get_flags(self):
        z = self._open_read()
        print(list(z[self.name_flags][:]))
        return list(z[self.name_flags][:])

    def get_flag(self, iloop):
        z = self._open_read()
        return z[self.name_flags][iloop]

    def set_flag(self, iloop, value=True):
        z = self._open_write()
        z[self.name_flags][iloop] = value

    def _open_read(self):
        import zarr

        return zarr.open(self.zarr_path, mode="r")

    def _open_write(self):
        import zarr

        return zarr.open(self.zarr_path, mode="r+")

    def create(self, lengths, overwrite=False):
        z = self._open_write()

        add_zarr_dataset(
            self.name_lengths,
            lengths,
            zarr_root=z,
            dtype="i4",
            overwrite=overwrite,
        )
        flags = add_zarr_dataset(
            self.name_flags,
            len(lengths) * [False],
            zarr_root=z,
            dtype=bool,
            overwrite=overwrite,
        )
        flags.attrs["_initialised"] = True

    def reset(self, lengths):
        return self.create(lengths, overwrite=True)


class ZarrLoader(Loader):
    writer = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.z = None
        self.statistics = []

    @classmethod
    def from_config(cls, *, config, path, **kwargs):
        # config is the path to the config file
        # or a dict with the config
        obj = cls(config=config, path=path, **kwargs)
        return obj

    @classmethod
    def from_zarr(cls, *, config, path, **kwargs):
        import zarr

        assert os.path.exists(path), path
        z = zarr.open(path, mode="r")
        # metadata = json.loads(z.attrs["_climetlab"])
        metadata = yaml.safe_load(z.attrs["_climetlab"])
        kwargs.get("print", print)("config loaded from zarr ", z.attrs["_climetlab"])
        config = metadata["create_yaml_config"]
        return cls.from_config(config=config, path=path, **kwargs)

    def iter_loops(self):
        if "loop" not in self.main_config or self.main_config.loop is None:
            raise NotImplementedError()
            yield None  # ?
            return

        for vars in self.main_config._iter_loops():
            yield vars

    def _compute_lengths(self, multiply):
        def squeeze_dict(dic):
            keys = list(dic.keys())
            assert len(dic) == 1, keys
            return dic[keys[0]]

        lengths = []
        for i, vars in enumerate(self.iter_loops()):
            lst = squeeze_dict(vars)
            assert isinstance(lst, (tuple, list)), lst
            lengths.append(len(lst))

        lengths = [x * multiply for x in lengths]
        return lengths

    def initialise(self):
        """Create empty zarr from self.main_config and self.path"""
        import zarr

        def get_one_element_config():
            for i, vars in enumerate(self.iter_loops()):
                keys = list(vars.keys())
                assert len(vars) == 1, keys
                key = keys[0]
                vars = {key: vars[key][0]}
                return self.main_config.substitute(vars)

        config = get_one_element_config()

        cube, grid_points = self.config_to_data_cube(config, with_gridpoints=True)

        shape = list(cube.extended_user_shape)
        # Notice that shape[0] can be >1
        # we are assuming that all data has the same shape
        one_element_length = shape[0]
        lengths = self._compute_lengths(one_element_length)

        shape[0] = sum(lengths)

        chunks = cube.chunking(self.main_config.output.chunking)
        dtype = self.main_config.output.dtype

        self.print(
            f"Creating ZARR '{self.path}', with {shape=}, " f"{chunks=} and {dtype=}"
        )
        self.z = zarr.open(self.path, mode="w")
        self.z.create_dataset("data", shape=shape, chunks=chunks, dtype=dtype)

        lat = self._add_dataset("latitude", grid_points[0])
        lon = self._add_dataset("longitude", grid_points[1])
        assert lat.shape == lon.shape

        metadata = {}
        metadata["create_yaml_config"] = _tidy(self.main_config)
        metadata["name_to_index"] = {
            name: i
            for i, name in enumerate(
                self.main_config.output.order_by[self.main_config.output.statistics]
            )
        }
        for k, v in self.main_config.get("metadata", {}).items():
            self.z.attrs[k] = v

        metadatastr = yaml.dump(metadata, sort_keys=False)
        # metadatastr = json.dumps(metadata, sort_keys=False)

        self.z.attrs["climetlab"] = metadata
        self.z.attrs["_climetlab"] = metadatastr
        self.z["data"].attrs["climetlab"] = metadata
        self.z["data"].attrs["_climetlab"] = metadatastr
        self.z.attrs["version"] = VERSION

        self.z = None

        self.registry.create(lengths=lengths)

    def config_to_data_cube(self, config, with_gridpoints=False):
        start = time.time()
        data = cml.load_source("loader", config.input)
        assert len(data), f"No data for {config}"
        self.print(f"Done in {seconds(time.time()-start)}, length: {len(data):,}.")

        start = time.time()
        self.print("Sorting dataset")
        cube = data.cube(
            config.output.order_by,
            remapping=config.output.remapping,
            flatten_values=config.output.flatten_values,
        )
        cube = cube.squeeze()
        self.print(f"Sorting done in {seconds(time.time()-start)}.")

        if not with_gridpoints:
            return cube
        else:
            return cube, data[0].grid_points()

    def _add_dataset(self, *args, **kwargs):
        import zarr

        z = self.z
        if z is None:
            z = zarr.open(self.path, mode="r+")

        return add_zarr_dataset(*args, **kwargs, zarr_root=z)

    def close(self):
        if self.writer is None:
            warnings.warn("FastWriter already closed")
        else:
            self.writer.flush()
            self.statistics.append(self.writer.stats(self.config.statistics_axis))

            self.writer = None

    def print_info(self):
        assert self.z is not None
        try:
            print(self.z["data"].info)
        except Exception as e:
            print(e)
        print("...")
        try:
            print(self.z["data"].info)
        except Exception as e:
            print(e)

    def add_statistics(self, **kwargs):
        import zarr

        if not all(self.registry.get_flags()):
            raise Exception(f"Zarr {self.path} is not fully built.")

        z_read = zarr.open(self.path, mode="r")
        data = z_read["data"]
        shape = data.shape
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
            self.print(f"Computing statistics on {i+1}/{shape[0]}")
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

        _count = data.size / shape[1]
        assert _count == int(_count), _count

        # self._add_dataset("mean_by_datetime", mean)
        # self._add_dataset("stdev_by_datetime", stdev)
        # self._add_dataset("minimum_by_datetime", minimum)
        # self._add_dataset("maximum_by_datetime", maximum)
        # self._add_dataset("sums_by_datetime", sum)
        # self._add_dataset("squares_by_datetime", squares)
        # self._add_dataset("count_by_datetime", mean * 0 + count)

        _minimum = np.amin(minimum, axis=0)
        _maximum = np.amax(maximum, axis=0)
        _sums = np.sum(sums, axis=0)
        _squares = np.sum(squares, axis=0)
        _mean = _sums / _count
        _stdev = np.sqrt(_squares / _count - _mean * _mean)

        _count = _mean * 0 + _count

        self._add_dataset("mean", _mean)
        self._add_dataset("stdev", _stdev)
        self._add_dataset("minimum", _minimum)
        self._add_dataset("maximum", _maximum)
        self._add_dataset("sums", _sums)
        self._add_dataset("squares", _squares)
        self._add_dataset("count", _count)


class HDF5Loader:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

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
