# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import os

import climetlab as cml

from .tools import parse_args


def _index_grib_file(path, path_name=None):
    import eccodes

    with open(path, "rb") as f:

        h = eccodes.codes_grib_new_from_file(f)

        while h:
            try:
                field = dict()

                if isinstance(path_name, str):
                    field["_path"] = path_name
                elif path_name is False:
                    pass
                elif path_name is None:
                    field["_path"] = path
                else:
                    raise ValueError(f"Value of path_name cannot be '{path_name}.'")

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

                field["_param_id"] = eccodes.codes_get_string(h, "paramId")
                field["param"] = eccodes.codes_get_string(h, "shortName")

                yield field

            finally:
                eccodes.codes_release(h)

            h = eccodes.codes_grib_new_from_file(f)


def _index_url(path_name, url):
    path = cml.load_source("url", url).path
    # TODO: or use download_and_cache?
    # path = download_and_cache(url)
    yield from _index_grib_file(path, path_name=path_name)


def _index_path(path):
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for name in files:
                yield from _index_grib_file(os.path.join(root, name))
    else:
        yield from _index_grib_file(path)


class GribCmd:
    @parse_args(
        paths_or_urls=dict(
            metavar="PATH_OR_URL",
            type=str,
            nargs="+",
            help="list of files or directories or urls to index",
        ),
        # json=dict(action="store_true", help="produce a JSON output"),
        baseurl=dict(
            metavar="BASEURL",
            type=str,
            help="Base url to use as a prefix to happen on each PATHS_OR_URLS to build urls.",
        ),
    )
    def do_index_gribs(self, args):
        """Create index files for grib files.
        If the option --baseurl is provided, create an index for multiple gribs.
        See https://climetlab.readthedocs.io/contributing/grib.html for details.
        """
        for path_or_url in args.paths_or_urls:
            if args.baseurl:
                entries = _index_url(
                    url=f"{args.baseurl}/{path_or_url}", path_name=path_or_url
                )
            elif os.path.exists(path_or_url):
                entries = _index_path(path_or_url)
            elif path_or_url.startswith("https://"):
                entries = _index_url(url=path_or_url, path_name=False)
            else:
                raise ValueError(f'Cannot find "{path_or_url}" to index it.')

            for e in entries:
                print(json.dumps(e))
