#!/usr/bin/env python
#
# (C) Copyright 2021- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#
import itertools
import logging
import os

from climetlab.utils import load_json_or_yaml
from climetlab.utils.humanize import did_you_mean

LOG = logging.getLogger(__name__)

ALIASES = {}


def _find_aliases(name):
    if name not in ALIASES:
        path = os.path.join(os.path.dirname(__file__), name + ".yaml")
        ALIASES[name] = load_json_or_yaml(path)
    return ALIASES[name]


def unalias(name, value):
    return _find_aliases(name).get(value, value)
