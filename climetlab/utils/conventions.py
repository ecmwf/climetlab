# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
import re
from collections import defaultdict

import yaml

from climetlab.decorators import locked

ALIASES = {}
CONVENTIONS = defaultdict(dict)
SEP = "@"


@locked
def get_alias_and_conventions():
    """ fill the global variable from the relevant yaml file """

    if ALIASES:
        return ALIASES, CONVENTIONS

    path = os.path.join(os.path.dirname(__file__), "conventions.yaml")
    with open(path) as f:
        mappings = yaml.load(f.read(), Loader=yaml.SafeLoader)["parameter_name"]

    def split_mapping(key):
        m = re.match(f"([^{SEP}]*){SEP}(.*)", key)
        if not m:
            return None, key
        return m.groups()

    for i, m in enumerate(mappings):
        for conv_key in m:
            convention, key = split_mapping(conv_key)
            if convention:
                CONVENTIONS[convention][i] = key
            ALIASES[key] = i

    return ALIASES, CONVENTIONS


def normalise_string(key, convention="cf"):
    aliases, conventions = get_alias_and_conventions()
    i = aliases.get(key, key)
    c = conventions[convention]
    new = c.get(i, key)
    logging.debug(f"Normalising '{key}' into '{new}' ({c} convention)")
    return new
