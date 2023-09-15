# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
from contextlib import contextmanager

from climetlab import settings
from climetlab.loaders import HDF5Loader, ZarrLoader
from climetlab.utils.humanize import list_to_human

from .tools import parse_args


class LoadersCmd:
    @parse_args(
        # dataset=(
        #     "--dataset",
        #     dict(
        #         help="Name of the HDF5 dataset to use"
        #         " (default from config or 'dataset')"
        #     ),
        # ),
        path=(
            "--target",
            dict(
                help="Where to store the final data. "
                "Currently only a path to a new ZARR is supported."
            ),
        ),
        init=(
            "--init",
            dict(action="store_true", help="Initialise zarr."),
        ),
        load=(
            "--load",
            dict(action="store_true", help="Load data into zarr."),
        ),
        statistics=(
            "--statistics",
            dict(action="store_true", help="Compute statistics."),
        ),
        config=(
            "--config",
            dict(
                help="Use with --init. A yaml file that describes which data to use as input"
                " and how to organise them in the target."
            ),
        ),
        parts=(
            "--parts",
            dict(nargs="+", help="Use with --load. Part(s) of the data to process."),
        ),
        cache_dir=(
            "--cache-dir",
            dict(
                help="Use with --load. Location of cache directory for temporary data."
            ),
        ),
        format=(
            "--format",
            dict(
                help="The format of the target storage into which to load the data"
                " (default is inferred from target path extension)"
                " only .zarr is currently supported."
            ),
        ),
        no_check=(
            "--no-check",
            dict(action="store_true", help="Skip checks."),
        ),
        force=(
            "--force",
            dict(action="store_true", help="Overwrite if already exists."),
        ),
        timeout=(
            "--timeout",
            dict(
                type=int,
                default=0,
                help="Stop with error (SIGALARM) after TIMEOUT seconds.",
            ),
        ),
    )
    def do_create(self, args):
        format = args.format

        if args.timeout:
            import signal

            signal.alarm(args.timeout)

        if format is None:
            _, ext = os.path.splitext(args.path)
            format = ext[1:]
        assert format == "zarr", f"Unsupported format={format}"

        def no_callback(*args, **kwargs):
            print(*args, **kwargs)
            return

        if os.environ.get("CLIMETLAB_CREATE_SHELL_CALLBACK"):

            def callback(*msg):
                msg = [str(_) for _ in msg]
                msg = "\n".join(msg)
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

            callback("Starting-zarr-loader.")
        else:
            callback = no_callback

        LOADERS = dict(
            zarr=ZarrLoader,
            h5=HDF5Loader,
            hdf5=HDF5Loader,
            hdf=HDF5Loader,
        )
        if format not in LOADERS:
            lst = list_to_human(list(LOADERS.keys()), "or")
            raise ValueError(f"Invalid format '{format}', must be one of {lst}.")

        kwargs = vars(args)
        kwargs["print"] = callback
        loader_class = LOADERS[format]

        lst = [args.load, args.statistics, args.init]
        if sum(1 for x in lst if x) != 1:
            raise ValueError(
                "Too many options provided."
                'Must choose exactly one option in "--load", "--statistics", "--init"'
            )
        if args.parts:
            assert args.load, "Use --parts only with --load"

        @contextmanager
        def dummy_context():
            yield

        context = dummy_context()
        if kwargs["cache_dir"]:
            context = settings.temporary("cache-directory", kwargs["cache_dir"])

        with context:
            if args.init:
                assert args.config, "--init requires --config"
                assert args.path, "--init requires --target"

                import zarr

                try:
                    zarr.open(args.path, "r")
                    if not args.force:
                        raise Exception(
                            f"{args.path} already exists. Use --force to overwrite."
                        )
                except zarr.errors.PathNotFoundError:
                    pass

                loader = loader_class.from_config(**kwargs)
                loader.initialise()
                exit()

            if args.load:
                assert (
                    args.config is None
                ), "--load requires only a --target, no --config."
                loader = loader_class.from_zarr(**kwargs)
                loader.load(**kwargs)

            if args.statistics:
                assert (
                    args.config is None
                ), "--statistics requires only --target, no --config."
                loader = loader_class.from_zarr(**kwargs)
                loader.add_statistics()
