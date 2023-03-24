# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

from climetlab.loaders import HDF5Loader, ZarrLoader, load
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
                help="The format of the storage into which to load the data"
                " (default is inferred from output path extension)"
            ),
        ),
        manifest=(
            "--manifest",
            dict(
                help="The format of the storage into which to load the data"
                " (default is inferred from output path extension)"
            ),
        ),
        path=(
            "--path",
            dict(
                help="Name of the HDF5 dataset to use (default from config or 'dataset')"
            ),
        ),
    )
    def do_load(self, args):
        if args.format is None:
            _, ext = os.path.splitext(args.path)
            args.format = ext[1:]

        LOADERS = dict(zarr=ZarrLoader, h5=HDF5Loader, hdf5=HDF5Loader, hdf=HDF5Loader)
        if args.format not in LOADERS:
            lst = list_to_human(list(LOADERS.keys()), "or")
            raise ValueError(f"Invalid format '{args.format}', must be one of {lst}.")

        return load(
            LOADERS[args.format](args.path),
            args.manifest,
            dataset=args.dataset,
        )
