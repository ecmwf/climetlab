import climetlab as cml

source = cml.load_source("file", "./docs/examples/test.grib")

with open(source, "rb") as f:
    print(f.read(1024))
