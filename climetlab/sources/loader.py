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

ACTIONS = {
    "source": load_source,
    "dataset": load_dataset,
}


class Loader(Source):
    def __init__(self, config):
        from climetlab.utils import load_json_or_yaml

        if isinstance(config, str):
            config = load_json_or_yaml(config)
        self.config = config

    def mutate(self):
        data = []
        inherit = False
        for k, v in self.config.items():
            if k == "inherit":
                inherit = v
            action = ACTIONS.get(k)
            if action is not None:
                if not isinstance(v, list):
                    v = [v]
                last = {}
                for one in v:
                    name = one.pop("name")
                    if inherit:
                        last.update(one)
                        one = last
                    LOG.debug(f"Using data from: {name}, {one}")
                    source = action(name, **one)
                    assert len(source), f"No data for {(action,name, one)}"
                    data.append(source)

        result = data[0]
        for d in data[1:]:
            result = result + d

        return result


source = Loader
