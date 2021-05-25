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
from climetlab.core.plugins import find_plugin, register
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


def _module_callback(plugin):
    return import_module(plugin, package=__name__).dataset


def camel(name):
    return "".join(x[0].upper() + x[1:].lower() for x in name.split("-"))


class YamlDefinedDataset(Dataset):
    def __init__(self):
        self.source = climetlab.load_source(self._src, **self._args)

    def __call__(self):
        return self


class DatasetLoader:

    kind = "dataset"

    def load_yaml(self, path):
        name, _ = os.path.splitext(os.path.basename(path))
        with open(path) as f:
            dataset = yaml.load(f.read(), Loader=yaml.SafeLoader)["dataset"]
            attributes = dataset.get("metadata", {})
            attributes.update(
                dict(_path=path, _src=dataset["source"], _args=dataset.get("args", {}))
            )
            return type(camel(name), (YamlDefinedDataset,), attributes)

    def load_module(self, module):
        return import_module(module, package=__name__).dataset

    def load_entry(self, entry):
        entry = entry.load()
        if callable(entry):
            return entry
        return entry.dataset


def register_dataset(module):
    register("dataset", module)


class DatasetMaker:
    def lookup(self, name):

        loader = DatasetLoader()
        klass = find_plugin(os.path.dirname(__file__), name, loader)

        return klass

    def __call__(self, name, *args, **kwargs):
        return self.lookup(name, *args, **kwargs)

    def __getattr__(self, name):
        return self(name.replace("_", "-"))


dataset = DatasetMaker()

TERMS_OF_USE_SHOWN = set()


def load_dataset(name, *args, **kwargs):

    klass = dataset.lookup(name)

    if name not in TERMS_OF_USE_SHOWN:
        if klass.terms_of_use is not None:
            print(klass.terms_of_use)
        TERMS_OF_USE_SHOWN.add(name)

    ds = klass(*args, **kwargs).mutate()
    if getattr(ds, "name", None) is None:
        ds.name = name
    return ds
