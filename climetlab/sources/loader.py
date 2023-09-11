# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from ..datasets import load_dataset
from ..sources import load_source
from . import Source

LOG = logging.getLogger(__name__)


class LoadAction:
    def execute(self, v, data, last, inherit):
        if not isinstance(v, list):
            v = [v]
        for one in v:
            one = dict(**one)
            name = one.pop("name")
            if inherit:
                last.update(one)
                one = last
            print(f"Using data from: {name}, {one}")
            source = self.load(name, **one)

            assert len(source), f"No data for {(name, one)}"
            data.append(source)


class LoadSource(LoadAction):
    def load(self, *args, **kwargs):
        return load_source(*args, **kwargs)


class LoadDataset(LoadAction):
    def load(self, *args, **kwargs):
        return load_dataset(*args, **kwargs)


class LoadConstants(LoadSource):
    def execute(self, v, data, last, inherit):
        super().execute(
            {
                "name": "constants",
                "source_or_dataset": data[0],
                "param": v,
            },
            data,
            last,
            inherit,
        )


ACTIONS = {
    "source": LoadSource,
    "dataset": LoadDataset,
    "constants": LoadConstants,
}


def instanciate_values(o, kwargs):
    if isinstance(o, dict):
        return {k: instanciate_values(v, kwargs) for k, v in o.items()}
    if isinstance(o, list):
        return [instanciate_values(v, kwargs) for v in o]
    if isinstance(o, tuple):
        return tuple([instanciate_values(v, kwargs) for v in o])
    if isinstance(o, str) and o.startswith("$"):
        return kwargs[o[1:]]
    return o


class Loader(Source):
    def __init__(self, config, **kwargs):
        from climetlab.utils import load_json_or_yaml

        if isinstance(config, str):
            config = load_json_or_yaml(config)
            if "input" in config:
                config = config["input"]
                config = instanciate_values(config, kwargs)

        assert isinstance(config, (list, tuple)), config

        self.config = config

    def mutate(self):
        """
        The config provided to this "loader" source can have
        multiple sources/datasets. Let's iterate along each of
        them, and concatenate them as a unique source.
        """
        data = []
        inherit = False
        last = {}
        for input in self.config:
            assert len(input) == 1, input
            assert isinstance(input, dict), input

            k = list(input.keys())[0]
            v = input[k]
            if k == "inherit":
                inherit = v
                continue

            ACTIONS[k]().execute(v, data, last, inherit)

        result = data[0]
        for d in data[1:]:
            result = result + d

        return result


source = Loader
