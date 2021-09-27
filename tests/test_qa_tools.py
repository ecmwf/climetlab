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
from importlib import import_module

import pytest
import yaml

from climetlab.testing import MISSING


def get_precommit_version(key):
    here = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(here, ".pre-commit-config.yaml")
    with open(path) as f:
        config = yaml.load(f.read(), Loader=yaml.SafeLoader)

    for c in config["repos"]:
        version = c.get("rev", None)
        for h in c.get("hooks"):
            if h.get("id", None) == key:
                return version
    return None


@pytest.mark.skipif(
    MISSING("black", "isort", "flake8"), reason="QA tools not installed"
)
def test_qa_versions():
    for name in ["black", "isort", "flake8"]:
        lib = import_module(name)
        required = get_precommit_version(name)
        installed = lib.__version__
        assert (
            installed == required
        ), f"Must use {name} version {required}. But version {installed} is installed."


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
