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
from climetlab.core.order import build_remapping
from climetlab.utils import load_json_or_yaml, progress_bar
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
        self.cache = np.zeros(shape)
        self.shape = shape

    def __setitem__(self, key, value):
        self.cache[key] = value

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


class ZarrLoader:
    def __init__(self, path):
        self.path = path
        self.z = None

    def create_array(self, dataset, shape, chunks, dtype, append, grid_points_first):
        import zarr

        print(
            f"Creating ZARR file '{self.path}', with {shape=}, {chunks=} and {dtype=}"
        )

        if append:
            self.z = zarr.open(self.path, mode="r+")

            original_shape = self.z.shape
            assert len(shape) == len(original_shape)

            axis = 1 if grid_points_first else 0

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
        self.writer.flush()

    def print_info(self):
        print(self.z.info)

    def add_metadata(self, config):
        import zarr

        if self.z is None:
            self.z = zarr.open(self.path, mode="r+")
            self.print_info()

        metadata = {}

        statistics = -1

        output = config["output"]
        order = output["order"]

        flatten_values = output.get("flatten_values", False)
        grid_points_first = output.get("grid_points_first", False)
        if grid_points_first and not flatten_values:
            raise NotImplementedError(
                "For now, grid_points_first is only valid if flatten_values"
            )

        statistics_axis = output.get("statistics")

        for i, k in enumerate(order):
            if isinstance(k, dict):
                if list(k.keys())[0] == statistics_axis:
                    statistics = i

        if statistics >= 0:
            axis = statistics + 1 if grid_points_first else statistics

            mean = stdev = minimum = maximum = self.z
            axis = tuple(i for i in range(len(self.z.shape)) if i != axis)

            start = time.time()

            print("Compute mean")
            mean = np.mean(mean, axis=axis)
            print(seconds(time.time() - start))
            start = time.time()
            print("Compute stdev")
            stdev = np.std(stdev, axis=axis)
            print(seconds(time.time() - start))
            start = time.time()
            print("Compute minimum")
            minimum = np.amin(minimum, axis=axis)
            print(seconds(time.time() - start))
            start = time.time()
            print("Compute maximum")
            maximum = np.amax(maximum, axis=axis)
            print(seconds(time.time() - start))

            statistics_names = list(order[statistics].values())[0]
            assert isinstance(statistics_names, list)
            assert len(statistics_names) == len(mean), (
                statistics_names,
                len(statistics_names),
                len(mean),
            )

            name_to_index = metadata["name_to_index"] = {}
            statistics_by_name = metadata["statistics_by_name"] = {}
            for i, name in enumerate(statistics_names):
                statistics_by_name[name] = {}
                statistics_by_name[name]["mean"] = mean[i]
                statistics_by_name[name]["stdev"] = stdev[i]
                statistics_by_name[name]["minimum"] = minimum[i]
                statistics_by_name[name]["maximum"] = maximum[i]
                name_to_index[name] = i

            statistics_by_index = metadata["statistics_by_index"] = {}
            statistics_by_index["mean"] = list(mean)
            statistics_by_index["stdev"] = list(stdev)
            statistics_by_index["maximum"] = list(maximum)
            statistics_by_index["minimum"] = list(minimum)

        metadata["config"] = _tidy(config)

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


def _load(loader, config, append, dataset=None):
    start = time.time()
    print("Loading dataset", config)

    data = cml.load_source("loader", config["input"])
    assert len(data), config["input"]
    print(f"Done in {seconds(time.time()-start)}, length: {len(data):,}.")

    output = config["output"]
    order = output["order"]

    flatten_values = output.get("flatten_values", False)
    grid_points_first = output.get("grid_points_first", False)
    if grid_points_first and not flatten_values:
        raise NotImplementedError(
            "For now, grid_points_first is only valid if flatten_values"
        )

    start = time.time()
    print("Sort dataset")
    cube = data.cube(
        order,
        remapping=build_remapping(output.get("remapping")),
        flatten_values=output.get("flatten_values", False),
        grid_points_first=grid_points_first,
    )
    cube = cube.squeeze()
    print(f"Done in {seconds(time.time()-start)}.")

    chunking = output.get("chunking", {})
    chunks = cube.chunking(chunking)

    dtype = output.get("dtype", "float32")
    if dataset is None:
        dataset = output.get("dataset", "dataset")

    array = loader.create_array(
        dataset,
        cube.extended_user_shape,
        chunks,
        dtype,
        append,
        grid_points_first,
    )

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
    config = load_json_or_yaml(config)

    if metadata_only:
        loader.add_metadata(config)
        return

    loop = config.get("loop")
    if loop is None:
        _load(loader, config, append, **kwargs)
    else:

        def loops():
            yield from (
                dict(zip(loop.keys(), items))
                for items in itertools.product(
                    expand(*list(loop.values())),
                )
            )

        for vars in loops():
            print(vars)
            _load(loader, substitute(config, vars), append=append, **kwargs)
            append = True

    loader.add_metadata(config)
