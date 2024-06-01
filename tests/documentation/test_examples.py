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

from climetlab.testing import IN_GITHUB
from climetlab.testing import climetlab_file

# import pytest


IGNORE = [
    "conf.py",
    "xml2rst.py",
    "actions.py",
    "generate-examples-maps.py",
    "settings-2-set.py",
]

EXAMPLES = climetlab_file("docs")


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


@pytest.mark.skipif(not IN_GITHUB, reason="Not on GITHUB")
@pytest.mark.parametrize("path", example_list())
@pytest.mark.documentation
def test_example(path):
    full = os.path.join(EXAMPLES, path)
    with open(full) as f:
        exec(f.read(), dict(__file__=full), {})


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
