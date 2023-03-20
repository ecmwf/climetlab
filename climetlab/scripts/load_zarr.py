# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import time

import climetlab as cml
from climetlab.utils import progress_bar
from climetlab.utils.humanize import seconds

from .tools import parse_args


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

        print(f"Creating zarr file '{args.path}', with chunks={chunks}")

        z = zarr.open(
            args.path,
            mode="w",
            shape=cube.extended_shape,
            chunks=chunks,
            dtype=config["output"]["dtype"],
        )
        z.attrs["climetlab"] = dict(coords=cube.coords)

        print()
        print(z.info)
        start = time.time()
        load = 0
        save = 0

        reading_chunks = None
        for cublet in progress_bar(
            total=cube.count(reading_chunks),
            iterable=cube.iterate_cubelets(reading_chunks),
        ):  # reading_chunks=["param"]):
            # print(f"writing: z[{cublet.extended_icoords}] = {cublet.to_numpy().shape}")

            now = time.time()
            data = cublet.to_numpy()
            load += time.time() - now

            now = time.time()
            z[cublet.extended_icoords] = data
            save += time.time() - now

        print()
        print(z.info)
        print()
        print(
            f"Elapsed: {seconds(time.time() - start)},"
            f" load time: {seconds(load)},"
            f" write time: {seconds(save)}."
        )
