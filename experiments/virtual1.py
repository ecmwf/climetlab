import time

from dask.distributed import Client, LocalCluster

import climetlab as cml

cluster = LocalCluster(n_workers=10, processes=False)
client = Client(cluster)


ds = cml.load_source("virtual", param="msl")
now = time.time()
print("a", len(ds), now)
x = ds.to_xarray()
print("b", time.time() - now)

y = x.msl
print(y.mean(dim="time").compute())
