# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging
import time

import climetlab as cml
from climetlab.utils import progress_bar
from climetlab.utils.humanize import seconds

from .tools import parse_args

LOG = logging.getLogger(__name__)


class LoadZarrCmd:
    @parse_args(
        config=(None, dict(metavar="CONFIG", type=str)),
        path=(None, dict(metavar="PATH", type=str)),
    )
    def do_zarr(self, args):
        import zarr

        from climetlab.utils import load_json_or_yaml

        config = load_json_or_yaml(args.config)

        data = cml.load_source("loader", config["input"])
        order = config["output"]["order"]

        cube = data.cube(order).squeeze()

        chunking = config["output"].get("chunking", {})
        chunks = cube.chunking(**chunking)

        dtype = config["output"].get("dtype", "float32")

        print(f"Creating ZARR file '{args.path}', with chunks={chunks}")

        z = zarr.open(
            args.path,
            mode="w",
            shape=cube.extended_user_shape,
            chunks=chunks,
            dtype=dtype,
        )
        z.attrs["climetlab"] = dict(coords=cube.user_coords)

        print()
        print(z.info)
        start = time.time()
        load = 0
        save = 0

        reading_chunks = None
        for cubelet in (
            pbar := progress_bar(
                total=cube.count(reading_chunks),
                iterable=cube.iterate_cubelets(reading_chunks),
                # reading_chunks=["param"]
            )
        ):
            now = time.time()
            pbar.set_description(f"Processing {cubelet}")
            data = cubelet.to_numpy()
            load += time.time() - now

            now = time.time()
            z[cubelet.extended_icoords] = data
            save += time.time() - now

        print()
        print(z.info)
        print()
        print(
            f"Elapsed: {seconds(time.time() - start)},"
            f" load time: {seconds(load)},"
            f" write time: {seconds(save)}."
        )
