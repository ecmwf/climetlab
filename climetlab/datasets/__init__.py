# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
from importlib import import_module

import yaml

import climetlab
from climetlab.core.metadata import annotate
from climetlab.core.plugins import find_plugin
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
    terms_of_use = None

    _source = None

    def __init__(self, *args, **kwargs):
        pass

    def mutate(self):
        # Give a chance to a subclass to change
        return self

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

    def sel(self, *args, **kwargs):
        return self.source.sel(*args, **kwargs)

    def to_numpy(self, *args, **kwargs):
        import numpy as np

        return np.array([s.to_numpy(*args, **kwargs) for s in self.source])

    def to_xarray(self, *args, **kwargs):
        return self.source.to_xarray(*args, **kwargs)

    def to_pandas(self, *args, **kwargs):
        return self.source.to_pandas(*args, **kwargs)

    def to_metview(self, *args, **kwargs):
        return self.source.to_metview(*args, **kwargs)

    def _repr_html_(self):
        return table(self)

    def annotate(self, data, **kargs):
        return annotate(data, self, **kargs)

    def read_csv_options(self, *args, **kwargs):
        return {}

    def read_zarr_options(self, *args, **kwargs):
        return {}

    def cfgrib_options(self, *args, **kwargs):
        return {}

    def post_xarray_open_dataset_hook(self, ds, *args, **kwargs):
        return ds


def _module_callback(plugin):
    return import_module(plugin, package=__name__).dataset


class YamlDefinedDataset(Dataset):
    def __init__(self, path, dataset):
        self._path = path
        for k, v in dataset.get("metadata", {}).items():
            setattr(self, k, v)
        self._src = dataset["source"]
        self._args = dataset.get("args", {})

    def __call__(self):
        self.source = climetlab.load_source(self._src, **self._args)
        return self

    def __repr__(self):
        return f"YAML[{self._path}]"


class DatasetLoader:

    kind = "dataset"

    def load_yaml(self, path):
        with open(path) as f:
            return YamlDefinedDataset(
                path, yaml.load(f.read(), Loader=yaml.SafeLoader)["dataset"]
            )

    def load_module(self, module):
        return import_module(module, package=__name__).dataset

    def load_entry(self, entry):
        return entry.load().dataset


class DatasetMaker:
    def __call__(self, name, *args, **kwargs):
        loader = DatasetLoader()
        klass = find_plugin(os.path.dirname(__file__), name, loader)

        dataset = klass(*args, **kwargs)

        if getattr(dataset, "name", None) is None:
            dataset.name = name

        return dataset

    def __getattr__(self, name):
        return self(name.replace("_", "-"))


dataset = DatasetMaker()

TERMS_OF_USE_SHOWN = set()


def load_dataset(name, *args, **kwargs):
    ds = dataset(name, *args, **kwargs)

    if name not in TERMS_OF_USE_SHOWN:
        if ds.terms_of_use is not None:
            print(ds.terms_of_use)
        TERMS_OF_USE_SHOWN.add(name)

    return ds.mutate()
