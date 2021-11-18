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
import csv
import logging
import os

from climetlab.utils import load_json_or_yaml

LOG = logging.getLogger(__name__)

ALIASES = {}


def load_csv(path):
    result = {}
    with open(path) as f:
        for row in csv.reader(f):
            result[row[0]] = row[1]

    return result


def _find_aliases(name):
    if name not in ALIASES:
        path = os.path.join(os.path.dirname(__file__), name)
        if os.path.exists(path + ".csv"):
            ALIASES[name] = load_csv(path + ".csv")
        else:
            ALIASES[name] = load_json_or_yaml(path + ".yaml")
    return ALIASES[name]


def unalias(name, value):
    return _find_aliases(name).get(value, value)


if __name__ == "__main__":
    print(unalias("grib-paramid", "2t"))
