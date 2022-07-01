# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging
import os

LOG = logging.getLogger(__name__)


def reader(source, path, magic=None, deeper_check=False):
    if magic is None or magic[:4] == b"GRIB":
        from .reader import GRIBReader

        return GRIBReader(source, path)


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
    import climetlab as cml

    path = cml.load_source("url", url).path
    # TODO: should use download_and_cache
    # path = download_and_cache(url)
    yield from _index_grib_file(path, path_name=path_name)


def _index_path(path):
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for name in files:
                yield from _index_grib_file(os.path.join(root, name))
    else:
        yield from _index_grib_file(path)


def _parse_files(directory, relative_paths, ignore=None):
    if ignore is None:
        ignore = []
    assert isinstance(ignore, (list, tuple))

    LOG.debug(f"Parsing files in {directory}")
    assert os.path.isdir(directory)

    for root, _, files in os.walk(directory):
        for name in files:
            if name in ignore:
                continue

            path = os.path.join(root, name)
            LOG.debug(f"Parsing file {path}")

            if relative_paths is True:
                _path = os.path.relpath(path, directory)
            elif relative_paths is False:
                _path = os.path.abspath(path)
            elif relative_paths is None:
                _path = path
            else:
                assert False, relative_paths

            yield from _index_grib_file(path, path_name=_path)
