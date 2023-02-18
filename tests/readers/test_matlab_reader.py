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

import numpy as np
import pytest

import climetlab as cml
from climetlab.testing import MISSING


@pytest.mark.skipif(MISSING("scipy"), reason="scipy not installed")
def test_matlab_1():
    here = os.path.dirname(__file__)
    testfile = os.path.join(here, "little_endian.mat")
    s = cml.load_source("file", testfile)
    arr = s.to_numpy(key="floats")
    ref = np.array([[2, 3], [3, 4]])
    assert (arr == ref).all(), (arr, ref)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
