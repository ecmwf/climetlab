# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from . import Reader


class GriddedReader(Reader):
    def to_xarray(self, **kwargs):
        import xarray as xr

        options = dict(
            backend_kwargs=self.open_mfdataset_backend_kwargs,
        )
        options.update(kwargs)
        return xr.open_mfdataset(
            self.path,
            engine=self.open_mfdataset_engine,
            **options,
        )
