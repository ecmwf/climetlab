from climetlab.datasets import dataset_, load_dataset

p = "sample-grib-data"


print(dir(dataset_(p)))
print(dataset_(p).source)
print(load_dataset(p).source)
