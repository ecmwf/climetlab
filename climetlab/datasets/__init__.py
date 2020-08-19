# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import numpy as np
import climetlab
from importlib import import_module
from climetlab.core.plugins import find_plugin
import os
import yaml


class Dataset:

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

    def _repr_markdown_(self):
        return """

| {name} |  |
| --- | --- |
| Home page | {home_page} |
| Documentation | {documentation} |
| Citation | {citation} |
| Licence | {licence} |
        """.format(
            name=self.name,
            home_page=self.home_page,
            licence=self.licence,
            citation="<pre>%s</pre>" % (self.citation.replace("\n", "<br>"),),
            documentation=self.documentation,
        )


def _module_callback(plugin):
    return import_module(plugin, package=__name__).dataset


def _yaml_callcack(plugin):
    with open(plugin) as f:
        dataset = yaml.load(f.read(), Loader=yaml.SafeLoader)["dataset"]

    class Wrapped(Dataset):
        def __init__(self, *args, **kwargs):
            self.source = climetlab.load_source(
                dataset["source"], **dataset.get("args", {})
            )

    return Wrapped


def _lookup(name):
    return find_plugin(
        os.path.dirname(__file__),
        name,
        module_callback=_module_callback,
        yaml_callcack=_yaml_callcack,
    )


def load(name, *args, **kwargs):
    dataset = _lookup(name)(*args, **kwargs)
    if dataset.name is None:
        dataset.name = name
    return dataset
