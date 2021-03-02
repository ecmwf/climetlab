# (C) Copyright 2021 ECMWF.
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


class Cache:
    def __init__(self, store):
        self._store = store

    def __contains__(self, key):
        # print("Cache.__contains__", key)
        return key in self._store

    def __getitem__(self, key):
        # print("Cache.__getitem__", key)
        data = self._store[key]
        # print(len(data))
        return data

    def keys(self):
        return self._store.keys()


class ZarrS3(DataSource):
    def __init__(self, urls, **kwargs):
        super().__init__(**kwargs)

        if not isinstance(urls, list):
            urls = [urls]

        def url_to_store(url):
            bits = url.split("/")

            url = "/".join(bits[:3])
            root = "/".join(bits[3:])

            fs = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": url})

            store = s3fs.S3Map(
                root=root,
                s3=fs,
                check=False,
            )

            store = Cache(store)

            return store

        stores = [url_to_store(url) for url in urls]

        #        self._ds = xr.open_zarr(cache)
        self._ds = xr.open_mfdataset(stores, engine="zarr")

    def to_xarray(self):
        return self._ds


source = ZarrS3
