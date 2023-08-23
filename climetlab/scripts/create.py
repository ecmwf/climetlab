# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

from climetlab.loaders import HDF5Loader, ZarrLoader
from climetlab.utils.config import LoadersConfig
from climetlab.utils.humanize import list_to_human

from .tools import parse_args


class LoadersCmd:
    @parse_args(
        dataset=(
            "--dataset",
            dict(
                help="Name of the HDF5 dataset to use"
                " (default from config or 'dataset')"
            ),
        ),
        format=(
            "--format",
            dict(
                help="The format of the target storage into which to load the data"
                " (default is inferred from target path extension)"
            ),
        ),
        config=(
            "--config",
            dict(
                help="A yaml file that describes which data to use as input"
                " and how to organise them in the target"
            ),
        ),
        target=(
            "--target",
            dict(
                help="Where to store the data. "
                "Currently only a path to a new ZARR or HDF5 file is supported."
            ),
        ),
        metadata=(
            "--metadata",
            dict(action="store_true", help="Update metadata."),
        ),
        partial_loop_chunk_size=(
            "--partial-loop-chunk-size",
            dict(
                metavar="N",
                default=1,
                type=int,
                help="Process partially the data, grouping loop items by groups (loop chunks) of size N.",
            ),
        ),
        partial_loop_chunk_number=(
            "--partial-loop-chunk-number",
            dict(
                metavar="I",
                type=int,
                help="Process partially the data, only the loop chunk number I.",
            ),
        ),
        total_loop_chunk_number=(
            "--total-loop-chunk-number",
            dict(
                action="store_true",
                help="Do not run anything. Returns the number of loop chunks.",
            ),
        ),
    )
    def do_create(self, args):
        if args.total_loop_chunk_number:
            config = LoadersConfig(args.config)
            print(config._len_of_iter_loops())
            return

        if args.format is None:
            _, ext = os.path.splitext(args.target)
            args.format = ext[1:]

        def no_callback(*args, **kwargs):
            return

        if os.environ.get("CLIMETLAB_CREATE_SHELL_CALLBACK"):

            def callback(msg):
                import shlex
                import subprocess
                import traceback

                cmd = os.environ.get("CLIMETLAB_CREATE_SHELL_CALLBACK")
                cmd = cmd.format(msg)
                try:
                    print(f"Running {cmd}")
                    args = shlex.split(cmd)  # shlex honors the quotes
                    subprocess.run(args)
                except Exception as e:
                    print(f"Exception when running {cmd}" + traceback.format_exc())
                    print(e)

            callback("Starting-loader.")
        else:
            callback = no_callback

        LOADERS = dict(
            zarr=ZarrLoader,
            h5=HDF5Loader,
            hdf5=HDF5Loader,
            hdf=HDF5Loader,
        )
        if args.format not in LOADERS:
            lst = list_to_human(list(LOADERS.keys()), "or")
            raise ValueError(f"Invalid format '{args.format}', must be one of {lst}.")

        loader = LOADERS[args.format](args.target, config=args.config)

        if args.metadata:
            loader.add_metadata()
            return

        loader.load(
            dataset=args.dataset,
            partial_loop_chunk_size=args.partial_loop_chunk_size,
            partial_loop_chunk_number=args.partial_loop_chunk_number,
            print=callback,
        )
        loader.add_metadata()
