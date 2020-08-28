# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import numpy as np
import climetlab
from importlib import import_module
from climetlab.core.plugins import find_plugin
import os
import yaml
from climetlab.utils.html import table


class Dataset:
    """
    Doc string for Dataset
    """

    name = None
    home_page = "-"
    licence = "-"
    documentation = "-"
    citation = "-"

    _source = None

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = source
        source.dataset = self

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

    def _repr_html_(self):
        return table(self)


def _module_callback(plugin):
    return import_module(plugin, package=__name__).dataset


class DatasetLoader:

    kind = "dataset"

    def load_yaml(self, path):
        with open(path) as f:
            dataset = yaml.load(f.read(), Loader=yaml.SafeLoader)["dataset"]

        class Wrapped(Dataset):
            def __init__(self, *args, **kwargs):

                for k, v in dataset.get("metadata", {}).items():
                    setattr(self, k, v)

                self.source = climetlab.load_source(
                    dataset["source"], **dataset.get("args", {})
                )

        return Wrapped

    def load_module(self, module):
        return import_module(module, package=__name__).dataset

    def load_entry(self, entry):
        return entry.load().dataset


def load(name, *args, **kwargs):
    loader = DatasetLoader()
    dataset = find_plugin(os.path.dirname(__file__), name, loader)
    dataset = dataset(*args, **kwargs)
    if getattr(dataset, "name", None) is None:
        dataset.name = name
    return dataset
