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
import tempfile

import numpy as np

import climetlab as cml


def test_latlon():
    data = np.random.random((181, 360))

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "a.grib")

        f = cml.new_grib_output(path, date=20010101)
        f.write(data, param="2t")
        f.close()

        ds = cml.load_source("file", path)
        print(ds[0])


if __name__ == "__main__":
    test_latlon()
    # from climetlab.testing import main

    # main(__file__)
