# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import weakref
from importlib import import_module

from climetlab.core.caching import cache_file
from climetlab.utils.html import table


def lookup(name):
    source = import_module(".%s" % (name.replace("-", "_"),), package=__name__)
    return source.source


def load(name, *args, **kwargs):
    source = lookup(name)(*args, **kwargs).mutate()
    if source.name is None:
        source.name = name
    return source


def list_entries():
    here = os.path.realpath(os.path.dirname(__file__))
    result = []

    for n in os.listdir(here):
        if n.startswith("."):
            continue

        if n.startswith("_"):
            continue

        if not n.endswith(".py"):
            continue

        result.append(n[:-3])

    return result


class DataSource:
    """
    Doc
    """

    name = None
    home_page = "-"
    licence = "-"
    documentation = "-"
    citation = "-"

    _dataset = None

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def mutate(self):
        # Give a chance to `multi` to change source
        return self

    def cache_file(self, *args, extension=".cache"):
        owner = self.name
        if self.dataset:
            owner = self.dataset.name
        if owner is None:
            owner = self.__class__.__name__.lower()
        return cache_file(owner, *args, extension=extension)

    @property
    def dataset(self):
        if self._dataset is None:
            return None
        return self._dataset()

    @dataset.setter
    def dataset(self, dataset):
        self._set_dataset(weakref.ref(dataset))

    def _set_dataset(self, dataset):
        self._dataset = dataset

    def _repr_html_(self):
        return table(self)

    def read_csv_options(self, *args, **kwargs):
        if self.dataset is None:
            return {}
        return self.dataset.read_csv_options(*args, **kwargs)

    def read_zarr_options(self, *args, **kwargs):
        if self.dataset is None:
            return {}
        return self.dataset.read_zarr_options(*args, **kwargs)

    def cfgrib_options(self, *args, **kwargs):
        if self.dataset is None:
            return {}
        return self.dataset.cfgrib_options(*args, **kwargs)

    def post_xarray_open_dataset_hook(self, ds, *args, **kwargs):
        if self.dataset is None:
            # print(f'from {self} no self.dataset {self.dataset}, no hook')
            return ds
        return self.dataset.post_xarray_open_dataset_hook(ds, *args, **kwargs)
