#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

import yaml


def test_yaml():
    yfile = os.path.dirname(__file__) + "/example.yaml"
    with open(yfile) as f:
        yaml.load(f.read(), Loader=yaml.SafeLoader)


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
