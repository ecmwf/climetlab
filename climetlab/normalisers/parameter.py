# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# from climetlab.utils.parameters import yaml_loader_from_cfgrib_TODO
import os
import yaml

# word2id = {
#'temperature' : 'temp_id123'
#'2t' : 'temp_id123'
#'t2m' : 'temp_id123'
# }
#
# CONVENTIONS = {}
# CONVENTIONS['mars'] = {
#    'temp_id123' : '2t'
# }

# word2id = {
#'temperature' : 'temp_id123'
#'2t' : 'temp_id123'
#'t2m' : 'temp_id123'
# }
#
# CONVENTIONS = {}
# CONVENTIONS['mars'] = {
#    'temp_id123' : '2t',
#    'temp_id45' : 'tp'
# }
# CONVENTIONS['cf'] = {
#    'temp_id123' : 't2m',
#    'temp_id45' : 'tp'
# }

ALIASES = None
CONVENTIONS = None


def get_alias_and_conventions(
    yaml_file=os.path.join(os.path.dirname(__file__), "parameter.yaml")
):
    """ fill the global variable from the relevant yaml file """
    global ALIASES
    global CONVENTIONS
    if ALIASES is None and CONVENTIONS is None:
        path = yaml_file
        with open(path) as f:
            mappings = yaml.load(f.read(), Loader=yaml.SafeLoader)

        def split_mapping(key):
            sep = ":"
            import re

            if sep in key:
                convention, rest = re.match(
                    f"([^{sep}]*){sep}([^{sep}]*)", key
                ).groups()
                return convention, rest
            else:
                return None, key

        CONVENTIONS = {"mars": {}, "cf": {}}
        ALIASES = {}
        for i, m in enumerate(mappings):
            for conv_key in m:
                convention, key = split_mapping(conv_key)
                if convention:
                    CONVENTIONS[convention][i] = key
                ALIASES[key] = i

    return ALIASES, CONVENTIONS


class ParameterNormaliser:
    def __init__(self, convention=None):
        self.convention = convention

    def normalise(self, parameter):
        if isinstance(parameter, (list, tuple)):
            return [self.normalise_param(p) for p in parameter]
        else:
            return self.normalise_param(parameter)

        return parameter

    def normalise_param(self, key):
        convention = self.convention
        ALIASES, CONVENTIONS = get_alias_and_conventions()
        i = ALIASES.get(key, key)
        c = CONVENTIONS[convention]
        return c.get(i, key)
