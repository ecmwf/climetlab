# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
from importlib import import_module

import yaml

import climetlab
from climetlab.core import Base
from climetlab.core.metadata import annotate
from climetlab.core.plugins import find_plugin
from climetlab.core.plugins import register as register_plugin
from climetlab.core.settings import SETTINGS
from climetlab.utils import download_and_cache
from climetlab.utils.html import table

LOG = logging.getLogger(__name__)


class Dataset(Base):
    """Mother class to create a dataset object."""

    name = None
    """ str : To be overrided by the class inherithing from Dataset.

    The name of the dataset.
    """

    home_page = "-"
    """ str : To be overrided by the class inherithing from Dataset.

    Contains a link to the home page related to the dataset.
    """

    licence = "-"
    """ str : To be overrided by the class inherithing from Dataset.

    Contains a link to the licence of the dataset.
    """

    documentation = "-"
    """ str : To be overrided by the class inherithing from Dataset.

    Contains a link to the documentation related to the dataset.
    """

    citation = "-"
    """ str : To be overrided by the class inherithing from Dataset.

    Contains the citation related to the dataset.
    """

    terms_of_use = None
    """ str : To be overrided by the class inherithing from Dataset.

    Contains the Terms of Use of the dataset.
    It will be shown to the user when they download the dataset for the first time.

    Uses :py:const:`TERMS_OF_USE_SHOWN`
    """

    _source = None

    def __init__(self, *args, **kwargs):
        """Do nothing. To be overridden by the inherithing class."""
        pass

    def mutate(self):
        """Give a chance to a subclass to change itself to another class after creation time.

        Returns
        -------
        self
        """
        return self

    @property
    def source(self):
        """Most methods are delegated to the ``source`` of the dataset.
        Returns
        -------
        :py:class:`Source`
        """
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

    def order_by(self, *args, **kwargs):
        return self.source.order_by(*args, **kwargs)

    @property
    def coords(self):
        return self.source.coords

    @property
    def all_coords(self):
        return self.source.all_coords

    def to_numpy(self, **kwargs):
        import numpy as np

        return np.array([s.to_numpy(**kwargs) for s in self.source])

    def to_xarray(self, **kwargs):
        return self.source.to_xarray(**kwargs)

    def to_tfdataset(self, **kwargs):
        return self.source.to_tfdataset(**kwargs)

    def to_pandas(self, **kwargs):
        return self.source.to_pandas(**kwargs)

    def to_metview(self, **kwargs):
        return self.source.to_metview(**kwargs)

    def _repr_html_(self):
        return table(self)

    def annotate(self, data, **kargs):
        return annotate(data, self, **kargs)


def _module_callback(plugin):
    return import_module(plugin, package=__name__).dataset


def camel(name):
    return "".join(x[0].upper() + x[1:].lower() for x in name.split("-"))


class YamlDefinedDataset(Dataset):
    """Dataset class to defined datasets from a YAML file.

    When inheriting, self._src and self._args must be defined before calling __init__.
    This is performed in :py:class:`DatasetLoader`.

    """

    def __init__(self):
        self.source = climetlab.load_source(self._src, **self._args)

    def __call__(self):
        return self


def _dataset_from_dict(name, dataset, path=None):
    attributes = dataset.get("metadata", {})
    attributes.update(
        dict(_path=path, _src=dataset["source"], _args=dataset.get("args", {}))
    )
    return type(camel(name), (YamlDefinedDataset,), attributes)


def dataset_from_dict(path, *args, **kwargs):
    return _dataset_from_dict(path)(*args, **kwargs).mutate()


def _dataset_from_yaml(path):
    name, _ = os.path.splitext(os.path.basename(path))
    with open(path) as f:
        dataset = yaml.load(f.read(), Loader=yaml.SafeLoader)["dataset"]
        return _dataset_from_dict(name, dataset, path)


def dataset_from_yaml(path, *args, **kwargs):
    return _dataset_from_yaml(path)(*args, **kwargs).mutate()


class DatasetLoader:

    kind = "dataset"

    def settings(self, name):
        return SETTINGS.get(name)

    def load_yaml(self, path):
        return _dataset_from_yaml(path)

    def load_module(self, module):
        return import_module(module, package=__name__).dataset

    def load_entry(self, entry):
        entry = entry.load()
        if callable(entry):
            return entry
        return entry.dataset

    def load_remote(self, name):
        catalogs = self.settings("datasets-catalogs-urls")
        for catalog in catalogs:
            url = f"{catalog}/{name}.yaml"
            path = download_and_cache(
                url,
                update_if_out_of_date=True,
                return_none_on_404=True,
            )

            if path:
                LOG.debug("Found dataset at %s", url)
                return self.load_yaml(path)

        return None


class DatasetMaker:
    def lookup(self, name):

        loader = DatasetLoader()
        klass = find_plugin(os.path.dirname(__file__), name, loader)

        return klass

    def __call__(self, name, *args, **kwargs):
        return self.lookup(name, *args, **kwargs)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return self(name.replace("_", "-"))


get_dataset = DatasetMaker()


TERMS_OF_USE_SHOWN = set()


def load_dataset(name: str, *args, **kwargs) -> Dataset:
    """Loads a dataset.

    Parameters
    ----------
    name : str
        Name of the dataset to be loaded.

    Returns
    -------
    Dataset
        The loaded dataset.
    """
    klass = get_dataset.lookup(name)

    if name not in TERMS_OF_USE_SHOWN:
        if klass.terms_of_use is not None:
            print(klass.terms_of_use)
        TERMS_OF_USE_SHOWN.add(name)

    ds = klass(*args, **kwargs).mutate()
    if getattr(ds, "name", None) is None:
        ds.name = name
    return ds


def register(name, proc):
    register_plugin("dataset", name, proc)
