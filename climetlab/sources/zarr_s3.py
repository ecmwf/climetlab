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
import s3fs


from . import DataSource

LOG = logging.getLogger(__name__)


class ZarrS3(DataSource):
    def __init__(self, url, root, **kwargs):

        super().__init__(**kwargs)

        fs = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": url})

        store = s3fs.S3Map(
            root=root,
            s3=fs,
            check=False,
        )
        self._ds = xr.open_zarr(store)

    def to_xarray(self):
        return self._ds


source = ZarrS3
