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

import yaml

# FIXME:
# from climetlab.decorators import locked

ALIASES = None
CONVENTIONS = None
DEFAULT_YAML_FILE = os.path.join(os.path.dirname(__file__), "conventions.yaml")
SEP = "@"


# @locked
def get_alias_and_conventions(yaml_file=DEFAULT_YAML_FILE):
    """ fill the global variable from the relevant yaml file """
    global ALIASES
    global CONVENTIONS
    if ALIASES is not None and CONVENTIONS is not None:
        return ALIASES, CONVENTIONS

    with open(yaml_file) as f:
        mappings = yaml.load(f.read(), Loader=yaml.SafeLoader)["parameter_name"]

    def split_mapping(key):

        if SEP in key:
            convention, rest = re.match(f"([^{SEP}]*){SEP}(.*)", key).groups()
            return convention, rest
        else:
            return None, key

    CONVENTIONS = dict()
    ALIASES = dict()
    for i, m in enumerate(mappings):
        for conv_key in m:
            convention, key = split_mapping(conv_key)
            if convention:
                if convention not in CONVENTIONS:
                    CONVENTIONS[convention] = {}
                CONVENTIONS[convention][i] = key
            ALIASES[key] = i

    return ALIASES, CONVENTIONS


def normalise_string(key, convention="cf"):
    ALIASES, CONVENTIONS = get_alias_and_conventions()
    i = ALIASES.get(key, key)
    c = CONVENTIONS[convention]
    new = c.get(i, key)
    logging.debug(f"Normalising '{key}' into '{new}' ({c} convention)")
    return new
