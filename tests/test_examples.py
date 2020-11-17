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

import pytest

IGNORE = ["conf.py", "xml2rst.py", "actions.py", "generate-examples-maps.py"]
EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")


def example_list():

    # return []

    examples = []
    for root, _, files in os.walk(EXAMPLES):
        for file in files:
            path = os.path.join(root, file)
            if path.endswith(".py") and file not in IGNORE:
                n = len(EXAMPLES) + 1
                examples.append(path[n:])

    return sorted(examples)


@pytest.mark.parametrize("path", example_list())
def test_example(path):

    full = os.path.join(EXAMPLES, path)
    with open(full) as f:
        exec(f.read(), dict(__file__=full), {})
