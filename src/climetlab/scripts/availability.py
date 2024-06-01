# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os

import climetlab as cml

from .tools import parse_args

LOG = logging.getLogger(__name__)


default_keys = ["param", "time", "date", "step", "levelist"]


class AvailabilityCmd:
    @parse_args(
        source=(
            None,
            dict(
                type=str,
                help="File or directory for describing a dataset or source of data with GRIB data.",
            ),
        ),
        stdout=dict(action="store_true", help="Output to stdout (no file)."),
        yaml=dict(action="store_true", help="Output yaml format."),
        keys=(
            "--keys",
            dict(
                type=str,
                help=f"Keys to use in availability default is ({','.join(default_keys)}).",
                nargs="+",
            ),
        ),
    )
    def do_availability(self, args):
        """Create json availability file."""

        keys = args.keys
        if keys == []:
            keys = default_keys

        if keys == ["*"]:
            keys = None

        self.avail = None

        path = args.source

        if not os.path.exists(path):
            print(f"{path} does not exists.")
            return

        if os.path.isdir(path):
            source = availability_of_directory(path)
        else:
            source = availability_of_file(path)

        availability = source._custom_availability(keys=keys)

        if args.yaml:
            print(availability.to_yaml())
            return

        if args.stdout:
            print(availability.tree())
            return

        # self.write(availability, source.availability_path)

    # def write(self, avail, output):
    #    if os.path.exists(output):
    #        i = 1
    #        while os.path.exists(f"{output}.{i}"):
    #            i += 1
    #        output = f"{output}.{i}"
    #        print(f"File already exists, writing to {output}")

    #    avail.to_pickle(output)


def availability_of_directory(dirpath):
    db_path = os.path.join(dirpath, "climetlab-2.db")
    if not os.path.exists(db_path):
        print(f"ERROR: this directory is not indexed yet, cannot find {db_path}.")

    source = cml.load_source("indexed-directory", dirpath)
    return source


def availability_of_file(path):
    # if magic = "SQLite"...
    return cml.load_source("file", path)
