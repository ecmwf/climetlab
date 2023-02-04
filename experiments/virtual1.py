# flake8: noqa
import os
import time

import dask

import climetlab as cml

ds = cml.load_source("virtual", param="2t")
now = time.time()
print("a", len(ds), now)
x = ds.to_xarray()
print(x)

y = x.t2m
print(y.mean(dim="time").compute())
