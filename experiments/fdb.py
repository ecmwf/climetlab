# flake8: noqa
#
# ret,param=t,grid=1/1,date=-2,target=data.grib,
# stream=enfo,number=1/to/50,type=pf
# FDB_ROOT_DIRECTORY=/tmp/fdb FDB_SCHEMA_FILE=~/build/fdb5/etc/fdb/schema  /usr/local/bin/fdb-write data.grib
#

import time

import climetlab as cml

now = time.time()
ds = cml.load_source(
    "fdb",
    root="/tmp/fdb",
    request={
        "class": "od",
        "type": "pf",
    },
)

print(ds.to_xarray())
print(time.time() - now)


print(ds.to_xarray().mean(dim="number"))
