# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

from .tools import parse_args


def _index_grib_file(path):
    import eccodes

    with open(path, "rb") as f:

        h = eccodes.codes_grib_new_from_file(f)

        while h:
            try:
                field = dict(_path=path)

                i = eccodes.codes_keys_iterator_new(h, "mars")
                try:
                    while eccodes.codes_keys_iterator_next(i):
                        name = eccodes.codes_keys_iterator_get_name(i)
                        value = eccodes.codes_get_string(h, name)
                        field[name] = value

                finally:
                    eccodes.codes_keys_iterator_delete(i)

                field["_offset"] = eccodes.codes_get_long(h, "offset")
                field["_length"] = eccodes.codes_get_long(h, "totalLength")

                yield field

            finally:
                eccodes.codes_release(h)

            h = eccodes.codes_grib_new_from_file(f)


def _index_path(path):
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for name in files:
                yield from _index_grib_file(os.path.join(root, name))
    else:
        yield from _index_grib_file(path)


class GribCmd:
    @parse_args(
        paths=dict(
            metavar="PATH",
            type=str,
            nargs="+",
            help="list of files or directories to index",
        ),
        # json=dict(action="store_true", help="produce a JSON output"),
    )
    def do_index_gribs(self, args):
        for path in args.paths:
            for n in _index_path(path):
                print(n)
