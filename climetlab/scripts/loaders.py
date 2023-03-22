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
import time

import numpy as np

import climetlab as cml
from climetlab.utils import load_json_or_yaml, progress_bar
from climetlab.utils.humanize import bytes, seconds

from .tools import parse_args


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


class LoadersCmd:
    @parse_args(
        dataset=(
            "--dataset",
            dict(
                help="Name of the HDF5 dataset to use (default from config or 'dataset')"
            ),
        ),
        config=(None, dict(metavar="CONFIG", type=str)),
        path=(None, dict(metavar="PATH", type=str)),
        verbose=dict(action="store_true"),
    )
    def do_hdf5(self, args):
        return self._loader(args, HDF5Loader(args.path))

    @parse_args(
        config=(None, dict(metavar="CONFIG", type=str)),
        path=(None, dict(metavar="PATH", type=str)),
        verbose=dict(action="store_true"),
    )
    def do_zarr(self, args):
        args.dataset = None
        return self._loader(args, ZarrLoader(args.path))

    def _loader(self, args, loader):
        config = load_json_or_yaml(args.config)

        data = cml.load_source("loader", config["input"])
        output = config["output"]
        order = output["order"]

        cube = data.cube(order).squeeze()

        chunking = output.get("chunking", {})
        chunks = cube.chunking(**chunking)

        dtype = output.get("dtype", "float32")
        if args.dataset is None:
            args.dataset = output.get("dataset", "dataset")

        array = loader.create_array(
            args.dataset,
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
            if args.verbose:
                print(cubelet, "mean=", cubelet.to_numpy().mean())
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
