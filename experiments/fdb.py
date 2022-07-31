# FDB_SCHEMA_FILE=~/build/fdb5/etc/fdb/schema  /usr/local/bin/fdb-write $(find . -name '*.grib')
import os

import climetlab as cml

ds = cml.load_source(
    "fdb",
    root="/tmp",
    schema=os.path.expanduser("~/build/fdb5/etc/fdb/schema"),
    request={"class": "od", "date": "20000101"},
)

print(ds.to_xarray())
