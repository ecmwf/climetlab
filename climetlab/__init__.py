# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from .arguments.transformers import ALL
from .core.caching import CACHE as cache
from .core.initialise import initialise
from .core.settings import SETTINGS as settings
from .datasets import Dataset
from .datasets import get_dataset as dataset  # so the user can do: cml.dataset(...)
from .datasets import load_dataset
from .distributed.dask import start_dask
from .plotting import interactive_map, new_plot, new_table
from .plotting import options as plotting_options
from .plotting import plot_graph, plot_map
from .readers import Reader
from .sources import Source
from .sources import get_source as source  # so the user can do: cml.source(...)
from .sources import load_source, load_source_lazily
from .version import __version__
from .wrappers import Wrapper

__all__ = [
    "ALL",
    "cache",
    "dataset",
    "Dataset",
    "Wrapper",
    "interactive_map",
    "load_dataset",
    "load_source",
    "load_source_lazily",
    "new_plot",
    "new_table",
    "plot_graph",
    "plot_map",
    "plotting_options",
    "Reader",
    "settings",
    "source",
    "Source",
    "start_dask",
    "__version__",
]


initialise()
