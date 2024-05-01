import os

import climetlab as cml
from climetlab.loaders import HDF5Loader
from climetlab.loaders import ZarrLoader
from climetlab.loaders import load

load(
    ZarrLoader("out.zarr"),
    os.path.join(os.path.dirname(__file__), "load-zarr-fourcastnet.yaml"),
)
