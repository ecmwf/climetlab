from dask.distributed import Client, LocalCluster

import climetlab as cml
import time

cluster = LocalCluster(n_workers=10, processes=False)
client = Client(cluster)


ds = cml.load_source("virtual")
print('a',len(ds), time.time())
x = ds.to_xarray()
print('b', time.time())
# print(x.chunks)

# print(x)

print(x.t2m)

y = x.t2m
# print(x.paramId_167.values)
print(y.mean(dim="time").compute())
