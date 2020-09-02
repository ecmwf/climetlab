# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from .sources import load as load_source
from .datasets import load as load_dataset
from .plotting import plot_map, new_plot
from .core.settings import SETTINGS as settings
from .core.caching import CACHE as cache

from climetlab.sources import DataSource
from climetlab.datasets import Dataset

__version__ = "0.0.76"


__all__ = [
    "load_source",
    "load_dataset",
    "plot_map",
    "new_plot",
    "settings",
    "cache",
    "Dataset",
    "DataSource",
]
