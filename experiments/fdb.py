import os
import time

from dask.distributed import Client, LocalCluster

import climetlab as cml

# FDB_SCHEMA_FILE=/Users/mab/build/fdb5/etc/fdb/schema  /usr/local/bin/fdb-write $(find . -name '*.grib')


cluster = LocalCluster(n_workers=10, processes=False)
client = Client(cluster)


ds = cml.load_source(
    "fdb",
    root="/tmp",
    schema=os.path.expanduser("~/build/fdb5/etc/fdb/schema"),
    request={'class':'od', 'date':'20000101'},
)
now = time.time()
print("a", len(ds), now)
x = ds.to_xarray()
print(x)
print("b", time.time() - now)
# exit(0)
# print(x.chunks)

# print(x)

print(x.t)

y = x.t
# print(x.paramId_167.values)
print(y.mean(dim="time").compute())
