# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

import xarray as xr
from xarray.backends.common import BackendEntrypoint

LOG = logging.getLogger(__name__)


# We wrap the sources because the FileSource is a os.PathLike and
# since version 0.20, xarray checks the class and change os.PathLike to
# strings. We don't want that, as we want to keep our objects
class WrappedSource:
    def __init__(self, source):
        self.source = source


class CMLEngine(BackendEntrypoint):
    @classmethod
    def open_dataset(cls, filename_or_obj, *args, **kwargs):
        assert isinstance(filename_or_obj, WrappedSource)
        return filename_or_obj.source.to_xarray()


def infer_open_mfdataset_kwargs(
    sources=None,
    paths=None,
    reader_class=None,
    user_kwargs={},
):
    result = {}
    result.update(user_kwargs.get("xarray_open_mfdataset_kwargs", {}))
    if False:
        ds = sources[0].to_xarray()
        # lat_dims = [s.get_lat_dim() for s in sources]

        if ds.dims == ["lat", "lon", "forecast_time"]:
            result["concat_dim"] = "forecast_time"

        result.update(user_kwargs)
    return result


def merge(
    sources=None,
    paths=None,
    reader_class=None,
    **kwargs,
):

    assert sources

    options = infer_open_mfdataset_kwargs(
        sources=sources,
        paths=paths,
        reader_class=reader_class,
        user_kwargs=kwargs,
    )

    if reader_class is not None and hasattr(
        reader_class, "to_xarray_multi_from_sources"
    ):
        return reader_class.to_xarray_multi_from_sources(
            sources,
            **options,
        )

    if paths is not None:
        if reader_class is not None and hasattr(
            reader_class, "to_xarray_multi_from_paths"
        ):
            return reader_class.to_xarray_multi_from_paths(
                paths,
                **options,
            )

        LOG.debug(f"xr.open_mfdataset with options={options}")
        return xr.open_mfdataset(paths, **options)

    LOG.debug(f"xr.open_mfdataset with options= {options}")
    return xr.open_mfdataset(
        [WrappedSource(s) for s in sources],
        engine=CMLEngine,
        **options,
    )
