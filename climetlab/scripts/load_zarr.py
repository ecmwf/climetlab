# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import climetlab as cml

from .tools import parse_args


class LoadZarrCmd:
    @parse_args(
        config=(None, dict(metavar="CONFIG", type=str)),
    )
    def do_zarr(self, args):
        data = cml.load_source("loader", args.config)
        print(data)
