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
    "cds",
    dataset="reanalysis-era5-single-levels",
    product_type="reanalysis",
    param="2t",
    grid="10/10",
    date="19590101/to/19590201",
    time=12,
)

df = ds.to_pandas(latitude=0.0, longitude=0.0)
print(df)
