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


class Loader:
    pass


VERSION = 2


class ZarrLoader(Loader):
    def __init__(self, path):
        self.path = path
        self.z = None
        self.statistics = []

    def create_array(self, config, cube, append, grid_points):
        import zarr

        self.config = config

        if not append:
            self.statistics = []

        shape = cube.extended_user_shape
        chunks = cube.chunking(config.output.chunking)
        dtype = config.output.dtype

        print(
            f"Creating ZARR file '{self.path}', with {shape=}, "
            f"{chunks=} and {dtype=}"
        )

        if append:
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

        else:
            self.z = zarr.open(self.path, mode="w")
            self.zdata = self.z.create_dataset(
                "data",
                shape=shape,
                chunks=chunks,
                dtype=dtype,
            )

            lat = self._add_dataset("latitude", grid_points[0])
            lon = self._add_dataset("longitude", grid_points[1])
            assert lat.shape == lon.shape

            self.writer = FastWriterWithCache(self.zdata, shape)

        return self.writer

    def _add_dataset(self, name, nparray, dtype=np.float32):
        assert len(nparray.shape) == 1, "Not implemented"
        a = self.z.create_dataset(
            name, shape=nparray.shape, dtype=dtype, overwrite=True
        )
        a[:] = nparray[:]
        return a

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

    def add_metadata(self, config):
        import zarr

        assert self.writer is None

        if self.z is None:
            self.z = zarr.open(self.path, mode="r+")
            self.print_info()

        metadata = {}

        count, sums, squares, minimum, maximum = self.statistics[0]
        for s in self.statistics[1:]:
            count = count + s[0]
            sums = sums + s[1]
            squares = squares + s[2]
            minimum = np.minimum(minimum, s[3])
            maximum = np.maximum(maximum, s[4])

        mean = sums / count
        stdev = np.sqrt(squares / count - mean * mean)

        name_to_index = {}
        statistics_by_name = {}
        for i, name in enumerate(self.config.statistics_names):
            statistics_by_name[name] = {}
            statistics_by_name[name]["mean"] = mean[i]
            statistics_by_name[name]["stdev"] = stdev[i]
            statistics_by_name[name]["minimum"] = minimum[i]
            statistics_by_name[name]["maximum"] = maximum[i]
            statistics_by_name[name]["sums"] = sums[i]
            statistics_by_name[name]["squares"] = squares[i]
            statistics_by_name[name]["count"] = count
            name_to_index[name] = i
        metadata["name_to_index"] = name_to_index
        metadata["statistics_by_name"] = statistics_by_name

        statistics_by_index = {}
        statistics_by_index["mean"] = list(mean)
        statistics_by_index["stdev"] = list(stdev)
        statistics_by_index["maximum"] = list(maximum)
        statistics_by_index["minimum"] = list(minimum)
        metadata["statistics_by_index"] = statistics_by_index

        self._add_dataset("mean", mean)
        self._add_dataset("stdev", stdev)
        self._add_dataset("minimum", minimum)
        self._add_dataset("maximum", maximum)
        self._add_dataset("sums", sums)
        self._add_dataset("squares", squares)
        self._add_dataset("count", mean * 0 + count)

        metadata["create_yaml_config"] = _tidy(config)
        for k, v in config.get("metadata", {}).items():
            self.z.attrs[k] = v

        self.z.attrs["climetlab"] = metadata
        self.z["data"].attrs["climetlab"] = metadata
        self.z.attrs["version"] = VERSION


class HDF5Loader:
    def __init__(self, path):
        self.path = path

    def create_array(
        self,
        dataset,
        shape,
        chunks,
        dtype,
        metadata,
        append,
        grid_points,
    ):
        import h5py

        if append:
            raise NotImplementedError("Appending do HDF5 not yet implemented")

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

    def add_metadata(self, config):
        warnings.warn("HDF5Loader.add_metadata not yet implemented")


def _load(loader, config, append, print_=print, **kwargs):
    start = time.time()
    print_("Loading input", config.input)

    data = cml.load_source("loader", config.input)

    if "constants" in config.input and config.input.constants:
        data = data + cml.load_source("constants", data, config.input.constants)

    assert len(data)
    print(f"Done in {seconds(time.time()-start)}, length: {len(data):,}.")

    start = time.time()
    print_("Sort dataset")
    cube = data.cube(
        config.output.order_by,
        remapping=config.output.remapping,
        flatten_values=config.output.flatten_values,
    )
    cube = cube.squeeze()
    print(f"Done in {seconds(time.time()-start)}.")

    grid_points = data[0].grid_points()
    array = loader.create_array(config, cube, append, grid_points)

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
    loader.close()
    save += time.time() - now

    print()
    loader.print_info()
    print()

    print(
        f"Elapsed: {seconds(time.time() - start)},"
        f" load time: {seconds(load)},"
        f" write time: {seconds(save)}."
    )


def load(loader, config, append=False, metadata_only=False, **kwargs):
    config = LoadersConfig(config)

    if metadata_only:
        loader.add_metadata(config)
        return

    if config.loop is None:
        assert not append, "Not yet implemented"
        _load(loader, config, append, **kwargs)
        loader.add_metadata(config)
        return

    for vars in config._iter_loops():
        print(vars)
        _load(loader, config.substitute(vars), append=append, **kwargs)
        loader.add_metadata(config)
        append = True
