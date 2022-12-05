# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import json
import logging
import os

from climetlab.utils.humanize import plural, seconds
import climetlab as cml

from .tools import parse_args

LOG = logging.getLogger(__name__)


class AvailabilityCmd:
    @parse_args(
        source=(
            None,
            dict(
                type=str,
                help="""
            File or directory for describing a dataset or source of data with GRIB data.
            """,
            ),
        )
    )
    def do_availability(self, args):
        """Create json availability file."""

        self.avail = None

        path = args.source

        if not os.path.exists(path):
            print(f"{path} does not exists.")

        if os.path.isdir(path):
            source = availability_of_directory(path)
            output = source.availability_path
        else:
            source = availability_of_file(path)
            output = os.path.join(path, ".availability.jsonl")

        self.write(source.availability, output)

    def write(self, avail, output):
        def output_path(path):
            if not os.path.exists(output):
                return output
            i = 1
            while os.path.exists(f"{output}.{i}"):
                i += 1
            print(f"File already exists, writing to {output}.{i}")
            return f"{output}.{i}"

        output = output_path(output)
        with open(output, "w") as f:
            f.write(avail.as_mars_list())


def availability_of_directory(dirpath):
    db_path = os.path.join(dirpath, "climetlab.db")
    if not os.path.exists(db_path):
        print("ERROR: this directory is not indexed yet, cannot find {db_path}.")

    source = cml.load_source("directory", dirpath)
    return source


def availability_of_file(path):
    # if magic = "SQLite"...
    return cml.load_source("file", path)
