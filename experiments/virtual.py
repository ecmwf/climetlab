import time

from dask.distributed import Client, LocalCluster

import climetlab as cml

cluster = LocalCluster(n_workers=10, processes=False)
client = Client(cluster)


ds = cml.load_source("virtual")
now = time.time()
print("a", len(ds), now)
x = ds.to_xarray()
print("b", time.time() - now)
# exit(0)
# print(x.chunks)

# print(x)

print(x.msl)

y = x.msl
# print(x.paramId_167.values)
print(y.mean(dim="time").compute())
