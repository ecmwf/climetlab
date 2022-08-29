# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import math
import warnings

from climetlab.utils.kwargs import Kwargs
from climetlab.utils.serialise import deserialise_state, serialise_state

LOG = logging.getLogger(__name__)


class ItemWrapperForCfGrib:
    def __init__(self, item, ignore_keys=[]):
        self.item = item
        self.ignore_keys = ignore_keys

    def __getitem__(self, n):
        if n in self.ignore_keys:
            return None
        if n == "values":
            return self.item.values
        return self.item.metadata(n)


class IndexWrapperForCfGrib:
    def __init__(self, index=None, ignore_keys=[]):
        self.index = index
        self.ignore_keys = ignore_keys

    def __getstate__(self):
        return dict(index=serialise_state(self.index), ignore_keys=self.ignore_keys)

    def __setstate__(self, state):
        self.index = deserialise_state(state["index"])
        self.ignore_keys = state["ignore_keys"]

    def __getitem__(self, n):
        return ItemWrapperForCfGrib(
            self.index[n],
            ignore_keys=self.ignore_keys,
        )

    def __len__(self):
        return len(self.index)


class XarrayMixIn:
    def xarray_open_dataset_kwargs(self):
        return dict(
            cache=True,  # Set to false to prevent loading the whole dataset
            chunks=None,  # Set to 'auto' for lazy loading
        )

    def to_xarray(self, **kwargs):

        import xarray as xr

        xarray_open_dataset_kwargs = {}

        if "xarray_open_mfdataset_kwargs" in kwargs:
            warnings.warn(
                "xarray_open_mfdataset_kwargs is deprecated, please use xarray_open_dataset_kwargs instead."
            )
            kwargs["xarray_open_dataset_kwargs"] = kwargs.pop(
                "xarray_open_mfdataset_kwargs"
            )

        user_xarray_open_dataset_kwargs = kwargs.get("xarray_open_dataset_kwargs", {})

        # until ignore_keys is included into cfgrib,
        # it is implemented here directly
        ignore_keys = user_xarray_open_dataset_kwargs.get("backend_kwargs", {}).pop(
            "ignore_keys", []
        )

        for key in ["backend_kwargs"]:
            xarray_open_dataset_kwargs[key] = Kwargs(
                user=user_xarray_open_dataset_kwargs.pop(key, {}),
                default={"errors": "raise"},
                forced={},
                logging_owner="xarray_open_dataset_kwargs",
                logging_main_key=key,
            )

        default = dict(squeeze=False)  # TODO:Documenet me
        default.update(self.xarray_open_dataset_kwargs())

        xarray_open_dataset_kwargs.update(
            Kwargs(
                user=user_xarray_open_dataset_kwargs,
                default=default,
                forced={
                    "errors": "raise",
                    "engine": "cfgrib",
                },
            )
        )

        result = xr.open_dataset(
            IndexWrapperForCfGrib(self, ignore_keys=ignore_keys),
            **xarray_open_dataset_kwargs,
        )

        def math_prod(lst):
            if not hasattr(math, "prod"):
                # python 3.7 does not have math.prod
                n = 1
                for x in lst:
                    n = n * x
                return n
            return math.prod(lst)

        def number_of_gribs(da):
            # Assumes last two dimensions are lat/lon coordinates
            skip = 2
            if da.dims[-1] == "values":
                # Assumes last dimension is the one-dimensional
                # lat/lon coordinate (non-regular grid)
                skip = 1
            return math_prod(list(da.shape)[:-skip])

        two_d_fields = sum(number_of_gribs(result[v]) for v in result.data_vars)

        # Make sure all the fields are converted
        # There may be more 2D xarray fields than GRB fields
        # if some missing dimension are filled with NaN values

        assert two_d_fields >= len(self), (
            "Not all GRIB fields were converted to xarray"
            f" ({len(self)} GRIBs > {two_d_fields} 2D-field(s) in xarray)"
        )

        return result
