# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import numpy as np
from importlib import import_module
from climetlab.core.plugins import find_plugin
import os


def lookup(name):
    plugin = find_plugin(os.path.dirname(__file__), name)
    dataset = import_module(plugin, package=__name__)
    return dataset.dataset


def load(name, *args, **kwargs):
    return lookup(name)(*args, **kwargs)


class Dataset:

    source = None

    def __len__(self):
        return len(self.source)

    def __getitem__(self, n):
        return self.source[n]

    def to_numpy(self, *args, **kwargs):
        return np.array([s.to_numpy(*args, **kwargs) for s in self.source])

    def to_xarray(self, *args, **kwargs):
        return self.source.to_xarray(*args, **kwargs)

    def to_pandas(self, *args, **kwargs):
        return self.source.to_pandas(*args, **kwargs)

    def to_metview(self, *args, **kwargs):
        return self.source.to_metview(*args, **kwargs)
