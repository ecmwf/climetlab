# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import sys

try:
    import ecmwflibs
# TODO: update when the version of Magics on conda is compatible with climetlab
# except ModuleNotFoundError:
#    # we rely on the library (libMagPlus) installed otherwise
#    pass
except Exception as e:
    print(
        f"Error importing ecmwflibs. Magics and/or eccodes may not be fonctionning? {e}",
        file=sys.stderr,
    )

from climetlab.datasets import Dataset
from climetlab.sources import DataSource

from .core.caching import CACHE as cache
from .core.metadata import init_metadata
from .core.settings import SETTINGS as settings
from .datasets import dataset, load_dataset
from .plotting import interactive_map, new_plot
from .plotting import options as plotting_options
from .plotting import plot_map
from .sources import load as load_source

__version__ = "0.3.18"


__all__ = [
    "load_source",
    "load_dataset",
    "dataset",
    "plot_map",
    "interactive_map",
    "new_plot",
    "settings",
    "cache",
    "Dataset",
    "DataSource",
    "plotting_options",
]

init_metadata()
