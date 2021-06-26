# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import itertools
import os

from .file import FileSource


def iterate_request(r):
    yield from (dict(zip(r.keys(), x)) for x in itertools.product(*r.values()))


def generate_grib(target, args):
    import eccodes

    handle = None
    try:
        with open(os.path.join(os.path.dirname(__file__), "dummy.grib"), "rb") as f:
            handle = eccodes.codes_new_from_file(f, eccodes.CODES_PRODUCT_GRIB)

        with open(target, "wb") as f:
            for r in iterate_request(args):
                for k, v in r.items():
                    eccodes.codes_set(handle, k, v)
                eccodes.codes_write(handle, f)

    finally:
        if handle is not None:
            eccodes.codes_release(handle)


def generate_unknown(target, args):
    import json

    with open(target, "w") as f:
        print(json.dumps(args), file=f)


GENERATORS = {
    "grib": (generate_grib, ".grib"),
    "unknown": (generate_unknown, ".unknown"),
}


class DummyGrib(FileSource):
    def __init__(self, kind, request=None, force=False, **kwargs):
        if request is None:
            request = {}
        request.update(kwargs)

        for k, v in list(request.items()):
            if not isinstance(v, (list, tuple)):
                request[k] = [v]

        generate, extension = GENERATORS[kind]

        self.path = self.cache_file(
            generate,
            request,
            hash_extra=kind,
            extension=extension,
            force=force,
        )


source = DummyGrib
