# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import os
import time

import numpy as np

import climetlab as cml
from climetlab.utils import progress_bar
from climetlab.utils.humanize import seconds, bytes

from .tools import parse_args


class LoadHDF5Cmd:
    @parse_args(
        config=(None, dict(metavar="CONFIG", type=str)),
        path=(None, dict(metavar="PATH", type=str)),
    )
    def do_hdf5(self, args):
        import h5py

        from climetlab.utils import load_json_or_yaml

        config = load_json_or_yaml(args.config)

        data = cml.load_source("loader", config["input"])
        order = config["output"]["order"]

        cube = data.cube(order).squeeze()

        chunking = config["output"].get("chunking", {})
        chunks = cube.chunking(**chunking)

        print(f"Creating HDF5 file '{args.path}', with chunks={chunks}")
        h5 = h5py.File(args.path, mode="w")

        dtype = config["output"].get("dtype", "float32")

        array = h5.create_dataset(
            "fields",
            chunks=chunks,
            maxshape=cube.extended_user_shape,
            dtype=dtype,
            data=np.empty(cube.extended_user_shape),  # Can we avoid that? Looks like its needed for chuncking
            # data = h5py.Empty(dtype),
        )

        start = time.time()
        load = 0
        save = 0

        reading_chunks = None
        for cublet in progress_bar(
            total=cube.count(reading_chunks),
            iterable=cube.iterate_cubelets(reading_chunks),
        ):

            now = time.time()
            data = cublet.to_numpy()
            load += time.time() - now

            now = time.time()
            array[cublet.extended_icoords] = data
            save += time.time() - now

        now = time.time()
        h5.close()
        save += time.time() - now

        print()
        size = os.path.getsize(args.path)
        print(f"HDF5 file {args.path}: {size:,} ({bytes(size)})")
        print()
        print(
            f"Elapsed: {seconds(time.time() - start)},"
            f" load time: {seconds(load)},"
            f" write time: {seconds(save)}."
        )
