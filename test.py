import climetlab as cml
import ecmwflibs

print(ecmwflibs.__file__)

source = cml.load_source("file", "/Users/baudouin/git/climetlab/docs/examples/test.grib")
for s in source:
    print(cml.plot_map(s))
#
