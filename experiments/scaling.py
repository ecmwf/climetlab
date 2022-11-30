# flake8: noqa
import climetlab as cml

request = dict(
    date="20220101/to/20220131",
    levtype="sfc",
    param="2t",
    grid="1/1",
)

ds = cml.load_source("mars", **request)

print(ds.statistics())
print(ds.to_bounding_box())
print(dir(ds))

s = ds.scaled(method="minmax")

print(s[0].to_numpy())
