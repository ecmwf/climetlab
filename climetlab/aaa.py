# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# This module is called aaa so isort keeps it at the top on the imports
# as it needs to run first

import sys

LOADED_MODULES = set()


class Requested:
    def find_spec(self, name, path=None, target=None):
        LOADED_MODULES.add(name)


class NotFound:
    def find_spec(self, name, path=None, target=None):
        LOADED_MODULES.discard(name)


def loaded_modules():
    global LOADED_MODULES
    return LOADED_MODULES


sys.meta_path.insert(0, Requested())
sys.meta_path.append(NotFound())
