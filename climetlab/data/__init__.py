# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#


import os
import yaml
import climetlab


def _find(collection, yaml_file, fail):
    top = os.path.dirname(climetlab.__file__)
    for path, dirs, files in os.walk(top):
        if os.path.basename(path) == collection:
            if yaml_file in files:
                return os.path.join(path, yaml_file)

    if fail:
        raise Exception("Cannot find '%s' in '%s'" % (yaml_file, collection))


def load(collection, name, fail=True):
    path = _find(collection, name + ".yaml", fail)
    if path is not None:
        with open(path) as f:
            return yaml.load(f.read(), Loader=yaml.SafeLoader)
