# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from ._version import __version__
from .aaa import loaded_modules
from .arguments.transformers import ALL
from .core.caching import CACHE as cache
from .core.constants import DATETIME
from .core.initialise import initialise
from .core.settings import SETTINGS as settings
from .datasets import Dataset
from .datasets import get_dataset as dataset  # so the user can do: cml.dataset(...)
from .datasets import load_dataset
from .distributed.dask import start_dask
from .plotting import interactive_map
from .plotting import new_plot
from .plotting import new_table
from .plotting import options as plotting_options
from .plotting import plot_map
from .readers import Reader
from .readers.grib.output import new_grib_coder
from .readers.grib.output import new_grib_output
from .sources import Source
from .sources import get_source as source  # so the user can do: cml.source(...)
from .sources import load_source
from .sources import load_source_lazily
from .wrappers import Wrapper

__all__ = [
    "__version__",
    "ALL",
    "cache",
    "dataset",
    "Dataset",
    "DATETIME",
    "interactive_map",
    "load_dataset",
    "load_source_lazily",
    "load_source",
    "loaded_modules",
    "new_grib_output",
    "new_grib_coder",
    "new_plot",
    "new_table",
    "plot_map",
    "plotting_options",
    "Reader",
    "settings",
    "source",
    "Source",
    "start_dask",
    "Wrapper",
]


initialise()
