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

TOP = os.path.dirname(os.path.dirname(__file__))

LANGUAGES = {".py": "python", ".yaml": "yaml"}


def execute(path):

    _, ext = os.path.splitext(path)

    print()
    print(".. code-block::", LANGUAGES[ext])
    print()

    with open(os.path.join(TOP, path)) as f:
        for line in f:
            print("    ", line.rstrip())

    print()
    print()


if __name__ == "__main__":
    execute("data/projections/global.yaml")
