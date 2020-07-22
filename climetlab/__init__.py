# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from .sources import load as load_source
from .datasets import load as load_dataset

# This is needed when running Sphinx on ReadTheDoc
try:
    from .plotting import plot_map
except ModuleNotFoundError:
    plot_map = None

__version__ = '0.0.3'

import climetlab.source
import climetlab.dataset


__all__ = [load_source,
           load_dataset,
           plot_map,
           climetlab.dataset,
           climetlab.source]
