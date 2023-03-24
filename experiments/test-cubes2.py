import os

import climetlab as cml
from climetlab.loaders import HDF5Loader, ZarrLoader, load

load(
    ZarrLoader("out.zarr"),
    os.path.join(os.path.dirname(__file__), "load-zarr-fourcastnet.yaml"),
)
