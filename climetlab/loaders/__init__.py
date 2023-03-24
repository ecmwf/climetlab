# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import json
import os
import re
import time

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

        def wrapped(name):
            def get(i, bit):
                p = func(bit) if i % 2 else bit
                return "" if p is None else str(p)

            if name in self.remapping:
                return "".join(
                    get(i, bit) for i, bit in enumerate(self.remapping[name])
                )

            return func(name)

        return wrapped


def build_remapping(mapping):
    def noop(x):
        return x

    if mapping is None:
        return noop

    if isinstance(mapping, dict):
        return Remapping(mapping)

    return mapping


class ZarrLoader:
    def __init__(self, path):
        self.path = path

    def create_array(self, dataset, shape, chunks, dtype, metadata):
        import zarr

        print(
            f"Creating ZARR file '{self.path}', with {shape=}, {chunks=} and {dtype=}"
        )

        self.z = zarr.open(
            self.path,
            mode="w",
            shape=shape,
            chunks=chunks,
            dtype=dtype,
        )

        self.z.attrs["climetlab"] = _tidy(metadata)

        return self.z

    def close(self):
        pass

    def print_info(self):
        print(self.z.info)


class HDF5Loader:
    def __init__(self, path):
        self.path = path

    def create_array(self, dataset, shape, chunks, dtype, metadata):
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


def load(loader, manifest, dataset=None):
    config = load_json_or_yaml(manifest)

    data = cml.load_source("loader", config["input"])
    output = config["output"]
    order = output["order"]

    cube = data.cube(
        order,
        remapping=Remapping(output.get("remapping")),
    )
    cube = cube.squeeze()

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
        config,
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
