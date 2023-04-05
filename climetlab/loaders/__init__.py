# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import datetime
import itertools
import json
import logging
import os
import re
import time
import warnings

import numpy as np

import climetlab as cml
from climetlab.core.order import build_remapping, normalize_order_by
from climetlab.utils import load_json_or_yaml, progress_bar
from climetlab.utils.humanize import bytes, seconds

LOG = logging.getLogger(__name__)


class Config:
    def __init__(self, config, **kwargs):
        if isinstance(config, str):
            config = load_json_or_yaml(config)
        self.config = config
        self.input = config["input"]
        self.output = config["output"]
        self.constants = config.get("constants")
        self.order = normalize_order_by(self.output["order"])
        self.remapping = build_remapping(self.output.get("remapping"))

        self.loop = self.config.get("loop")
        self.chunking = self.output.get("chunking", {})
        self.dtype = self.output.get("dtype", "float32")

        self.flatten_values = self.output.get("flatten_values", False)
        self.grid_points_first = self.output.get("grid_points_first", False)
        if self.grid_points_first and not self.flatten_values:
            raise NotImplementedError(
                "For now, grid_points_first is only valid if flatten_values"
            )

        # The axis along which we append new data
        # TODO: assume grid points can be 2d as well
        self.append_axis = 1 if self.grid_points_first else 0

        self.collect_statistics = False
        if "statistics" in self.output:
            statistics_axis_name = self.output["statistics"]
            statistics_axis = -1
            for i, k in enumerate(self.order):
                if k == statistics_axis_name:
                    statistics_axis = i

            assert statistics_axis >= 0, (statistics_axis_name, self.order)

            self.statistics_names = self.order[statistics_axis_name]

            # TODO: consider 2D grid points
            self.statistics_axis = (
                statistics_axis + 1 if self.grid_points_first else statistics_axis
            )
            self.collect_statistics = True

    def substitute(self, vars):
        def substitute(x, vars):
            if isinstance(x, (tuple, list)):
                return [substitute(y, vars) for y in x]

            if isinstance(x, dict):
                return {k: substitute(v, vars) for k, v in x.items()}

            if isinstance(x, str):
                if not re.match(r"\$(\w+)", x):
                    return x
                lst = []
                for i, bit in enumerate(re.split(r"\$(\w+)", x)):
                    if i % 2:
                        lst.append(vars[bit])
                    else:
                        lst.append(bit)

                lst = [e for e in lst if e != ""]

                if len(lst) == 1:
                    return lst[0]

                return "".join(str(_) for _ in lst)

            return x

        return Config(substitute(self.config, vars))


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
        self.cache = np.zeros(shape)
        self.shape = shape

    def __setitem__(self, key, value):
        self.cache[key] = value

    def flush(self):
        self.array[:] = self.cache[:]

    def stats(self, axis):
        sel = [slice(None)] * len(self.shape)
        sums = np.zeros(self.shape[axis])
        squares = np.zeros(self.shape[axis])
        minima = np.zeros(self.shape[axis])
        maxima = np.zeros(self.shape[axis])
        count = None
        for k in range(self.shape[axis]):
            sel[axis] = k
            values = self.cache[tuple(sel)]
            sums[k] = np.sum(values)
            squares[k] = np.sum(values * values)
            minima[k] = np.amin(values)
            maxima[k] = np.amax(values)
            if count is None:
                count = values.size
            else:
                assert count == values.size

        return (count, sums, squares, minima, maxima)


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


class ZarrLoader(Loader):
    def __init__(self, path):
        self.path = path
        self.z = None
        self.statistics = []

    def create_array(self, config, cube, append):
        import zarr

        self.config = config

        if not append:
            self.statistics = []

        shape = cube.extended_user_shape
        chunks = cube.chunking(config.chunking)
        dtype = config.dtype

        print(
            f"Creating ZARR file '{self.path}', with {shape=}, "
            f"{chunks=} and {dtype=}"
        )

        if append:
            self.z = zarr.open(self.path, mode="r+")

            original_shape = self.z.shape
            assert len(shape) == len(original_shape)

            axis = config.append_axis

            new_shape = []
            for i, (o, s) in enumerate(zip(original_shape, shape)):
                if i == axis:
                    new_shape.append(o + s)
                else:
                    assert o == s, (original_shape, shape, i)
                    new_shape.append(o)

            self.z.resize(tuple(new_shape))

            self.writer = FastWriter(
                OffsetView(
                    self.z,
                    original_shape[axis],
                    axis,
                    shape,
                ),
                shape,
            )

        else:
            self.z = zarr.open(
                self.path,
                mode="w",
                shape=shape,
                chunks=chunks,
                dtype=dtype,
            )

            self.writer = FastWriter(self.z, shape)

        return self.writer

    def close(self):
        if self.writer is None:
            warnings.warn("FastWriter already closed")
        else:
            self.writer.flush()
            if self.config.collect_statistics:
                self.statistics.append(self.writer.stats(self.config.statistics_axis))

            self.writer = None

    def print_info(self):
        print(self.z.info)

    def add_metadata(self, config):
        import zarr

        assert self.writer is None

        if self.z is None:
            self.z = zarr.open(self.path, mode="r+")
            self.print_info()

        metadata = {}

        if config.collect_statistics:
            count, sums, squares, minimum, maximum = self.statistics[0]
            for s in self.statistics[1:]:
                count = count + s[0]
                sums = sums + s[1]
                squares = squares + s[2]
                minimum = np.minimum(minimum, s[3])
                maximum = np.maximum(maximum, s[4])

            mean = sums / count
            stdev = np.sqrt(squares / count - mean * mean)

            name_to_index = metadata["name_to_index"] = {}
            statistics_by_name = metadata["statistics_by_name"] = {}
            for i, name in enumerate(self.config.statistics_names):
                statistics_by_name[name] = {}
                statistics_by_name[name]["mean"] = mean[i]
                statistics_by_name[name]["stdev"] = stdev[i]
                statistics_by_name[name]["minimum"] = minimum[i]
                statistics_by_name[name]["maximum"] = maximum[i]
                statistics_by_name[name]["sums"] = sums[i]
                statistics_by_name[name]["squares"] = sums[i]
                statistics_by_name[name]["count"] = count
                name_to_index[name] = i

            statistics_by_index = metadata["statistics_by_index"] = {}
            statistics_by_index["mean"] = list(mean)
            statistics_by_index["stdev"] = list(stdev)
            statistics_by_index["maximum"] = list(maximum)
            statistics_by_index["minimum"] = list(minimum)

        metadata["config"] = _tidy(config.config)

        self.z.attrs["climetlab"] = metadata


class HDF5Loader:
    def __init__(self, path):
        self.path = path

    def create_array(
        self, dataset, shape, chunks, dtype, metadata, append, grid_points_first
    ):
        import h5py

        if append:
            raise NotImplementedError("Appending do HDF5 not yet implemented")

        if grid_points_first:
            raise NotImplementedError("grid_points_first in HDF5 not yet implemented")

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


def _load(loader, config, append, **kwargs):
    start = time.time()
    print("Loading input", config.input)

    data = cml.load_source("loader", config.input)
    if config.constants:
        data = data + cml.load_source("constants", data, config.constants)

    assert len(data)
    print(f"Done in {seconds(time.time()-start)}, length: {len(data):,}.")

    start = time.time()
    print("Sort dataset")
    cube = data.cube(
        config.order,
        remapping=config.remapping,
        flatten_values=config.flatten_values,
        grid_points_first=config.grid_points_first,
    )
    cube = cube.squeeze()
    print(f"Done in {seconds(time.time()-start)}.")

    array = loader.create_array(config, cube, append)

    start = time.time()
    load = 0
    save = 0

    reading_chunks = None
    for cubelet in progress_bar(
        total=cube.count(reading_chunks),
        iterable=cube.iterate_cubelets(reading_chunks),
    ):
        now = time.time()
        data = cubelet.to_numpy()
        load += time.time() - now

        # print("data", data.shape,cubelet.extended_icoords)

        now = time.time()
        array[cubelet.extended_icoords] = data
        save += time.time() - now

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


def expand(values):
    if isinstance(values, list):
        return values

    if isinstance(values, dict):
        if "start" in values and "stop" in values:
            start = values["start"]
            stop = values["stop"]
            step = values.get("step", 1)
            return range(start, stop + 1, step)

        if "monthly" in values:
            start = values["monthly"]["start"]
            stop = values["monthly"]["stop"]
            date = start
            last = None
            result = []
            lst = []
            while True:
                year, month = date.year, date.month
                if (year, month) != last:
                    if lst:
                        result.append([d.isoformat() for d in lst])
                    lst = []

                lst.append(date)
                last = (year, month)
                date = date + datetime.timedelta(days=1)
                if date > stop:
                    break
            if lst:
                result.append([d.isoformat() for d in lst])
            return result

    raise ValueError(f"Cannot expand loop from {values}")


def load(loader, config, append=False, metadata_only=False, **kwargs):
    config = Config(config)

    if metadata_only:
        loader.add_metadata(config)
        return

    if config.loop is None:
        assert not append, "Not yet implemented"
        _load(loader, config, append, **kwargs)
        loader.add_metadata(config)
        return

    def loops():
        yield from (
            dict(zip(config.loop.keys(), items))
            for items in itertools.product(
                expand(*list(config.loop.values())),
            )
        )

    for vars in loops():
        print(vars)
        _load(loader, config.substitute(vars), append=append, **kwargs)
        loader.add_metadata(config)
        append = True
