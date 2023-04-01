#!/usr/bin/env python3

# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

import pytest


# Make sure all these modules are loaded lazily
# To find the culprit, rerun with:
# CLIMETLAB_DEBUG_IMPORTS=1 pytest tests/test_imports.py
@pytest.mark.parametrize(
    "module",
    [
        "pandas",
        "xarray",
        "eccodes",
        "Magics",
        "IPython",
        "jupyter",
        "torch",
        "tensorflow",
    ],
)
@pytest.mark.skipif(
    int(os.environ.get("SKIP_TEST_IMPORTS", "1")),
    reason="Only activated if SKIP_TEST_IMPORTS=0",
)
def test_imports(module):
    import climetlab as cml
    from climetlab.aaa import loaded_modules

    # This will trigger the loading of wrappers
    cml.load_source("file", __file__)

    modules = loaded_modules()

    assert module not in modules, "\n".join(modules[module])


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
