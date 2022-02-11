# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
from urllib.parse import urlparse

import s3fs
import xarray as xr
import zarr

from . import Source

LOG = logging.getLogger(__name__)


class Cache:
    def __init__(self, store):
        self._store = store

    def __contains__(self, key):
        LOG.debug("S3 Cache.__contains__ %s", key)
        return key in self._store

    def __getitem__(self, key):
        LOG.debug("S3 Cache.__getitem__ %s", key)
        data = self._store[key]
        LOG.debug("S3 Cache.__getitem__ %d", len(data))
        return data

    def keys(self):
        return self._store.keys()


def url_to_s3_store(url, user=None, password=None):
    bits = url.split("/")
    if bits[0] == "s3:":
        bits[0] = "https:"

    url = "/".join(bits[:3])
    root = "/".join(bits[3:])

    fs = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": url})

    store = s3fs.S3Map(
        root=root,
        s3=fs,
        check=False,
    )

    store = Cache(store)

    store = zarr.storage.KVStore(store)

    return store


def find_store(store):
    o = urlparse(store)

    if "@" in o.netloc:
        auth, server = o.netloc.split("@")
        user, password = auth.split(":")

    if o.scheme in ["http", "https", "s3"]:
        return url_to_s3_store(store)
    if os.path.exists(store):
        if store.endswith(".zip"):
            return zarr.ZipStore(store)
        return store
    if o.scheme in ["file"]:
        # hard coded 3 because urlparse plays with the initial /
        return store[(len(o.scheme) + 3) :]

    raise NotImplementedError(f"Unknown protocol '{o.scheme}' for Zarr in {store}")


class Zarr(Source):
    def __init__(self, store, **kwargs):
        super().__init__(**kwargs)

        self._url = None

        if isinstance(store, str):
            self._url = store
            store = find_store(store)

        try:
            self._ds = xr.open_dataset(store, engine="zarr")  # TODO: chunks="auto" ?
        except zarr.errors.GroupNotFoundError as e:
            if self._url:
                LOG.error("ERROR : Cannot find data from %s", self._url)
            raise (e)
        except PermissionError as e:
            if self._url:
                LOG.error("ERROR : Permission denied on accessing %s", self._url)
            raise (e)
        except Exception as e:
            if self._url:
                LOG.error("ERROR when accessing %s", self._url)
            raise (e)

    def to_xarray(self):
        return self._ds


# this is already in Multi
# dsdict = {}
# for ds in dslist:
#     for value in ds[concat_dim].values:
#         dsdict[value] = ds.sel(**{concat_dim: value})
#     values_sorted = sorted(dsdict.keys())
#     dslist = [dsdict[d] for d in values_sorted]

# self._ds = xr.concat(dslist, dim=concat_dim)
# # self._ds = xr.open_mfdataset(stores, engine="zarr", combine='nested')


source = Zarr
