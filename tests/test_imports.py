#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import pytest

import climetlab as cml
from climetlab.utils import module_loaded


# Make sure all these modules are loaded lazily
@pytest.mark.parametrize(
    "module",
    [
        "pandas",
        "xarray",
        "eccodes",
        "magics",
        "IPython",
        "jupyter",
        "torch",
        "tensorflow",
    ],
)
def test_imports(module):
    # This will trigger the loading of wrappers
    cml.load_source("file", __file__)

    assert not module_loaded(module)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
