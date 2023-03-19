# (C) Copyright 2023 European Centre for Medium-Range Weather Forecasts.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import torch

from .utils import as_numpy_func, default_merger


class TorchDataset(torch.utils.data.Dataset):
    def __init__(self, owner, elements):
        self.owner = owner
        self.elements = elements

    def __len__(self):
        return len(self.owner)

    def __getitem__(self, i):
        return self.elements.get_torch_item(i)
        # return self.owner.get_torch_item(i)


def build_data_specs(*args, output, **kwargs):
    return {
        "x,y": XYDataIO,
        "x": XDataIO,
        # TODO: einops style:
        #  "(bs, lat * lon, param * lev)":
        #  "(bs, lat * lon, param_lev)":
        #  "bs, (lat lon), (param lev)":
        #  "bs, (param lev), (lat lon)":
        # plev vs lev ?
        # param_plev ?
    }[output](*args, **kwargs)


class DataIO:
    def __init__(self, *args, owner=None, **kwargs):
        assert not args, "only keywords args are supported"
        self.owner = owner

        self.args = args
        self.kwargs = kwargs

    def merge_elements(self, elements, merger):
        funcs = [elt.func for name, elt in elements.items()]
        return merger(*funcs)

    def get_torch_item(self, key):
        raise NotImplementedError()


class XDataIO(DataIO):
    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, owner=owner, **kwargs)

        self._features = {}

        self.feature_options = kwargs.get("features_options", {})
        self.features_merger = kwargs.get("features_merger", default_merger)

        for name in kwargs["features"]:
            options = self.feature_options.get(name, {})
            self._features[name] = Element(name, owner, options).mutate()

        self.func = self.merge_elements(self._features, self.features_merger)

    def get_torch_item(self, key):
        return self.func(key)


class XYDataIO(DataIO):
    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, owner=owner, **kwargs)

        self._features = {}
        self._targets = {}

        self.feature_options = kwargs.get("features_options", {})
        self.target_options = kwargs.get("target_options", {})
        self.features_merger = kwargs.get("features_merger", default_merger)
        self.targets_merger = kwargs.get("targets_merger", default_merger)

        for name in kwargs["features"]:
            options = self.feature_options.get(name, {})
            self._features[name] = Element(name, owner, options).mutate()

        for name in kwargs["targets"]:
            options = self.feature_options.get(name, {})
            self._targets[name] = Element(name, owner, options).mutate()

        self.func = self.merge_elements(self._features, self.features_merger)
        self.target_func = self.merge_elements(self._targets, self.targets_merger)

    def get_torch_item(self, key):
        return self.func(key), self.target_func(key)


class Element:
    def __init__(self, string, dataset_or_source, options):
        self.dataset_or_source = dataset_or_source
        self._source = None
        self._init_string = string
        self.options = options

        self.name = string
        assert self.name is not None

    @property
    def source(self):
        if self._source is None:
            self._source = self.dataset_or_source.build_source_for_element(self)
        return self._source

    def get_item(self, i):
        return self.source[i]

    def mutate(self):
        return self

    @property
    def func(self):
        return as_numpy_func(self.source, self.options)  # refactor HERE TODO
