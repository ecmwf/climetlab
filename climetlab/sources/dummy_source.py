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

from climetlab.core.temporary import temp_directory

from .file import FileSource


def zip_dir(target, directory):
    with zipfile.ZipFile(target, "w") as z:
        for root, _, files in os.walk(directory):
            for f in files:
                fullpath = os.path.join(root, f)
                relpath = os.path.relpath(fullpath, start=directory)
                z.write(
                    fullpath,
                    arcname=relpath,
                    compress_type=zipfile.ZIP_DEFLATED,
                )


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


def make_xarray(
    variables=["a"],
    dims=["lat", "lon"],
    size=2,
    coord_values=None,
    attributes=None,
    **kwargs,
):
    import numpy as np
    import xarray as xr

    if isinstance(dims, (list, tuple)):
        dims = {k: dict(size=size) for k in dims}

    all_dims = list(dims.keys())

    if isinstance(variables, (list, tuple)):
        variables = {k: dict(dims=all_dims) for k in variables}

    coords = {}
    for d, args in dims.items():
        _size = args["size"]
        coords[d] = np.arange(_size, dtype=float)
        if coord_values and d in coord_values:
            coords[d] = coord_values[d]

    vars = {}
    for v, args in variables.items():
        _dims = variables[v]["dims"]
        _coords = {k: coords[k] for k in _dims}
        _shape = [dims[d]["size"] for d in _dims]
        data = np.arange(np.prod(_shape)).reshape(_shape)  # .as_type(float)
        arr = xr.DataArray(
            data,
            dims=_dims,
            coords=_coords,
        )
        vars[v] = arr

    ds = xr.Dataset(vars)

    if "lat" in ds.dims:
        ds["lat"].attrs["standard_name"] = "latitude"
    if "lon" in ds.dims:
        ds["lon"].attrs["standard_name"] = "longitude"
    if "time" in ds.dims:
        ds["time"].attrs["standard_name"] = "time"

    if attributes:
        for d, attrs in attributes.items():
            for k, v in attrs.items():
                ds[d].attrs[k] = v

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


def generate_csv(
    target,
    headers=None,
    lines=[],
    separator=",",
    quote_strings=None,
    none_are_empty=True,
    **kwargs,
):
    assert none_are_empty
    with open(target, "w") as f:
        if headers:
            print(separator.join(headers), file=f)

        def str_or_none(x):
            if x is None:
                return ""
            return str(x)

        def repr_or_none(x):
            if x is None:
                return ""
            return repr(x)

        _ = repr_or_none if quote_strings else str_or_none

        for line in lines:
            print(separator.join(_(x) for x in line), file=f)


def generate_zip(target, sources=None, names=None, directory=None, **kwargs):
    if sources is not None:
        assert directory is None
        assert names is not None
        assert len(sources) == len(names)
        with temp_directory() as tmpdir:
            for s, n in zip(sources, names):
                s.save(os.path.join(tmpdir, n))
            zip_dir(target, tmpdir)
            return

    if directory is not None:
        assert sources is None
        assert names is None
        zip_dir(target, directory)
        return

    assert False


GENERATORS = {
    "csv": (generate_csv, ".csv"),
    "grib": (generate_grib, ".grib"),
    "netcdf": (generate_netcdf, ".nc"),
    "unknown": (generate_unknown, ".unknown"),
    "zarr-zip": (generate_zarr_zip, ".zarr.zip"),
    "zarr": (generate_zarr, ".zarr"),
    "zeros": (generate_zeros, ".zeros"),
    "zip": (generate_zip, ".zip"),
}


class DummySource(FileSource):
    def __init__(self, kind, request=None, force=False, extension=None, **kwargs):
        super().__init__()

        if request is None:
            request = {}
        request.update(kwargs)

        generate, ext = GENERATORS[kind]
        if extension is not None:
            ext = extension

        def _generate(target, args):
            return generate(target, **args)

        self.path = self.cache_file(
            _generate,
            request,
            hash_extra=kind,
            extension=ext,
            force=force,
        )


source = DummySource
