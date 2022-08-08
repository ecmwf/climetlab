# import time

from dask.distributed import Client, LocalCluster

import climetlab as cml

cluster = LocalCluster(n_workers=10, processes=False)
client = Client(cluster)


ds = cml.load_source("virtual")
# now = time.time()
# print("a", len(ds), now)
# x = ds.to_xarray()
# print("b", time.time() - now)


# print(x.msl)

# y = x.msl
# print(y.mean(dim="time").compute())


tf = ds.to_tfdataset()
print(dir(tf))
for p in tf.take(1).as_numpy_iterator():
    print(p)
