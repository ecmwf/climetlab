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

MAGICS_KEYS = None

_inited = False


def init():
    global _inited, MAGICS_KEYS

    if not _inited:

        MAGICS_KEYS = defaultdict(set)
        with open(os.path.join(os.path.dirname(__file__), "magics.yaml")) as f:
            magics = yaml.load(f, Loader=yaml.SafeLoader)
            for action, params in magics.items():
                for param in params:
                    MAGICS_KEYS[param["name"]].add(action)

    _inited = True


def magics_keys_to_actions():
    init()
    return MAGICS_KEYS
