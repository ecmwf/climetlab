# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

import s3fs
import xarray as xr

from . import Source

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


class ZarrS3(Source):
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

        # adding a new dimension take a lot of memory
        # dslist = [xr.open_dataset(url_to_store(url), engine="zarr") for url in urls]
        # self._ds = xr.concat(dslist, dim = 'head_time')
        # return self._ds

        options = self.read_zarr_options()

        concat_dim = options.get("concat_dim", "forecast_time")

        stores = [url_to_store(url) for url in urls]

        dslist = []
        import zarr

        for store, url in zip(stores, urls):
            try:
                dslist.append(xr.open_dataset(store, engine="zarr", chunks="auto"))
            except zarr.errors.GroupNotFoundError as e:
                print(f"ERROR : Cannot find data at url = {url}")
                raise (e)

        assert len(dslist) > 0

        if len(dslist) == 1:
            self._ds = dslist[0]
        else:
            dsdict = {}
            for ds in dslist:
                for value in ds[concat_dim].values:
                    dsdict[value] = ds.sel(**{concat_dim: value})
                values_sorted = sorted(dsdict.keys())
                dslist = [dsdict[d] for d in values_sorted]

            self._ds = xr.concat(dslist, dim=concat_dim)
            # self._ds = xr.open_mfdataset(stores, engine="zarr", combine='nested')

    def to_xarray(self):
        self._ds = self.post_xarray_open_dataset_hook(self._ds)
        return self._ds


source = ZarrS3
