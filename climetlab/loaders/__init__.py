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
import os
import re
import time
import warnings

import numpy as np

import climetlab as cml
from climetlab.utils import load_json_or_yaml, progress_bar
from climetlab.utils.humanize import bytes, seconds


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


class Remapping:
    def __init__(self, remapping):
        self.remapping = {}

        for k, v in remapping.items():
            m = re.split(r"\{([^}]*)\}", v)
            self.remapping[k] = m

    def __call__(self, func):
        if self.remapping is None:
            return func

        class CustomJoiner:
            def format_name(self, x):
                return func(x)

            def format_string(self, x):
                return str(x)

            def join(self, args):
                return "".join(str(x) for x in args)

        joiner = CustomJoiner()

        def wrapped(name):
            return self.substitute(name, joiner)

        return wrapped

    def substitute(self, name, joiner):
        if name in self.remapping:
            lst = []
            for i, bit in enumerate(self.remapping[name]):
                if i % 2:
                    p = joiner.format_name(bit)
                    if p is not None:
                        lst.append(p)
                    else:
                        lst = lst[:-1]
                else:
                    lst.append(joiner.format_string(bit))
            return joiner.join(lst)
        return joiner.format_name(name)

    def as_dict(self):
        return self.remapping


def build_remapping(mapping):
    if mapping is None:
        return Remapping({})

    if isinstance(mapping, dict):
        return Remapping(mapping)

    return mapping


class OffsetView:
    def __init__(self, array, offset):
        self.array = array
        self.offset = offset

    def __setitem__(self, key, value):
        key = (key[0] + self.offset,) + key[1:]
        self.array[key] = value


class ZarrLoader:
    def __init__(self, path):
        self.path = path

    def create_array(self, dataset, shape, chunks, dtype, append):
        import zarr

        print(
            f"Creating ZARR file '{self.path}', with {shape=}, {chunks=} and {dtype=}"
        )

        if append:
            self.z = zarr.open(self.path, mode="r+")

            original_shape = self.z.shape

            assert original_shape[1:] == shape[1:]

            new_shape = (original_shape[0] + shape[0],) + shape[1:]

            self.z.resize(new_shape)

            return OffsetView(self.z, original_shape[0])

        else:
            self.z = zarr.open(
                self.path,
                mode="w",
                shape=shape,
                chunks=chunks,
                dtype=dtype,
            )

            return self.z

    def close(self):
        pass

    def print_info(self):
        print(self.z.info)

    def add_metadata(self, config):
        metadata = {}

        statistics = -1

        statistics_axis = config.get("statistics")
        output = config["output"]
        order = output["order"]

        for i, k in enumerate(order):
            if isinstance(k, dict):
                if list(k.keys())[0] == statistics_axis:
                    statistics = i

        if statistics >= 0:
            mean = stdev = minimum = maximum = self.z
            for i in range(len(self.z.shape)):
                if i == statistics:
                    continue
                mean = np.mean(mean, axis=i, keepdims=True)
                stdev = np.std(stdev, axis=i, keepdims=True)
                minimum = np.amin(minimum, axis=i, keepdims=True)
                maximum = np.amax(maximum, axis=i, keepdims=True)

            mean = mean.flatten()
            stdev = stdev.flatten()
            minimum = minimum.flatten()
            maximum = maximum.flatten()

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

    def create_array(self, dataset, shape, chunks, dtype, metadata, append):
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


def _load(loader, config, append, dataset=None):
    start = time.time()
    print("Loading dataset", config)

    data = cml.load_source("loader", config["input"])
    assert len(data), config["input"]
    print(f"Done in {seconds(time.time()-start)}, length: {len(data)}.")

    output = config["output"]
    order = output["order"]

    start = time.time()
    print("Sort dataset")
    cube = data.cube(
        order,
        remapping=Remapping(output.get("remapping")),
    )
    cube = cube.squeeze()
    print(f"Done in {seconds(time.time()-start)}.")

    chunking = output.get("chunking", {})
    chunks = cube.chunking(**chunking)

    dtype = output.get("dtype", "float32")
    if dataset is None:
        dataset = output.get("dataset", "dataset")

    array = loader.create_array(
        dataset,
        cube.extended_user_shape,
        chunks,
        dtype,
        append,
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


def load(loader, config, append=False, **kwargs):
    config = load_json_or_yaml(config)
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
