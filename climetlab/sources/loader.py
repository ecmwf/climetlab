# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import logging

import yaml

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
        if isinstance(config, str):
            with open(config, "r") as f:
                if config.endswith(".json"):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)

        self.config = config

    def mutate(self):
        data = []
        for k, v in self.config.items():
            action = ACTIONS.get(k)
            if action is not None:
                if not isinstance(v, list):
                    v = [v]
                for one in v:
                    data.append(action(one["name"], **one["request"]))

        return load_source("multi", data)


source = Loader
