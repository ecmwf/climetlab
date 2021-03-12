# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import os
from collections import defaultdict

import yaml

from climetlab.decorators import locked

MAGICS_KEYS = None
MAGICS_DEF = None
MAGICS_PARAMS = None
_inited = False


@locked
def init():
    global _inited, MAGICS_KEYS, MAGICS_DEF, MAGICS_PARAMS

    if not _inited:

        MAGICS_KEYS = defaultdict(set)
        MAGICS_PARAMS = defaultdict(dict)
        with open(os.path.join(os.path.dirname(__file__), "magics.yaml")) as f:
            MAGICS_DEF = yaml.load(f, Loader=yaml.SafeLoader)
            for action, params in MAGICS_DEF.items():
                for param in params:
                    name = param["name"]
                    MAGICS_KEYS[name].add(action)
                    MAGICS_PARAMS[action][name] = param

    _inited = True


def magics_keys_to_actions():
    init()
    return MAGICS_KEYS


def magics_keys_definitions():
    init()
    return MAGICS_DEF


def magics_keys_parameters(name):
    init()
    return MAGICS_PARAMS[name]
