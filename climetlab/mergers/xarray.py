# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import xarray as xr
from xarray.backends.common import BackendEntrypoint


class CMLEngine(BackendEntrypoint):
    @classmethod
    def open_dataset(cls, filename_or_obj, *args, **kwargs):
        return filename_or_obj.to_xarray()


def infer_open_mfdataset_kwargs(sources, user_kwargs):
    result = {}
    ds = sources[0].to_xarray()
    # lat_dims = [s.get_lat_dim() for s in sources]

    if ds.dims == ["lat", "lon", "forecast_time"]:
        result["concat_dim"] = "forecast_time"

    result.update(user_kwargs)
    return result


def to_xarray(self, *args, **kwargs):

    options = infer_open_mfdataset_kwargs(self.sources, kwargs)

    if False:  # all self sources is path:
        return xr.open_mfdataset([s.path for s in self.sources], **options)
    else:
        return xr.open_mfdataset(self.sources, engine=CMLEngine, **options)


def merge(
    source=None,
    paths=None,
    readers=None,
    **kwargs,
):
    pass
