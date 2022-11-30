# flake8: noqa
import os

import climetlab as cml

here = os.path.dirname(__file__)

ds = cml.load_source(
    "cds",
    "reanalysis-era5-single-levels",
    variable=["msl", "2t"],
    product_type="reanalysis",
    area=[50, -50, 20, 50],
    date="2012-12-12",
    time=list(reversed(range(24))),
)
for x in ds:
    print(x)
print("====")

for x in ds.order_by("param", "time"):
    print(x)
