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
import zipfile

from climetlab.core.temporary import temp_chdir, temp_directory

from .file import FileSource


def zip_dir(target, directory):
    z = zipfile.ZipFile(target, "w")
    with temp_chdir(directory):

        for root, _, files in os.walk("."):
            for f in files:
                fullname = os.path.join(root, f)
                z.write(fullname)
        z.close()


def iterate_request(r):
    yield from (dict(zip(r.keys(), x)) for x in itertools.product(*r.values()))


def generate_grib(target, **kwargs):
    import eccodes

    for k, v in list(kwargs.items()):
        if not isinstance(v, (list, tuple)):
            kwargs[k] = [v]

    handle = None
    try:
        with open(os.path.join(os.path.dirname(__file__), "dummy.grib"), "rb") as f:
            handle = eccodes.codes_new_from_file(f, eccodes.CODES_PRODUCT_GRIB)

        with open(target, "wb") as f:
            for r in iterate_request(kwargs):
                for k, v in r.items():
                    eccodes.codes_set(handle, k, v)
                eccodes.codes_write(handle, f)

    finally:
        if handle is not None:
            eccodes.codes_release(handle)


def generate_unknown(target, **kwargs):
    import json

    with open(target, "w") as f:
        print(json.dumps(kwargs), file=f)


def generate_zeros(target, size=1024 * 1024, chunk_size=1024 * 1024, **kwargs):

    chunk_size = min(chunk_size, size)
    zeros = bytes(chunk_size)

    with open(target, "wb") as f:
        while size > 0:
            bufsize = min(size, chunk_size)
            f.write(zeros[:bufsize])
            size -= bufsize


def make_xarray(variables=["a"], **kwargs):
    import numpy as np
    import xarray as xr

    lat = [0.0, 10.0, 20.0]
    lon = [0.0, 10.0]
    seed = xr.DataArray(
        np.zeros((3, 2)),
        dims=["lat", "lon"],
        coords={"lat": lat, "lon": lon},
    )

    vars = {}
    for i, v in enumerate(variables):
        vars[v] = seed + 1

    ds = xr.Dataset(vars)

    return ds


def generate_zarr(target, **kwargs):
    ds = make_xarray(**kwargs)
    ds.to_zarr(target)


def generate_zarr_zip(target, **kwargs):
    ds = make_xarray(**kwargs)
    with temp_directory() as tmpdir:
        ds.to_zarr(tmpdir)
        zip_dir(target, tmpdir)


def generate_netcdf(target, **kwargs):
    ds = make_xarray(**kwargs)
    ds.to_netcdf(target)


GENERATORS = {
    "grib": (generate_grib, ".grib"),
    "unknown": (generate_unknown, ".unknown"),
    "zeros": (generate_zeros, ".zeros"),
    "zarr": (generate_zarr, ".zarr"),
    "netcdf": (generate_netcdf, ".nc"),
    "zarr-zip": (generate_zarr_zip, ".zarr.zip"),
}


class DummySource(FileSource):
    def __init__(self, kind, request=None, force=False, **kwargs):
        if request is None:
            request = {}
        request.update(kwargs)

        generate, extension = GENERATORS[kind]

        def _generate(target, args):
            return generate(target, **args)

        self.path = self.cache_file(
            _generate,
            request,
            hash_extra=kind,
            extension=extension,
            force=force,
        )


source = DummySource
