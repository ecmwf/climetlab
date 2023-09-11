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
import sys
import tempfile

import numpy as np
import pytest

import climetlab as cml

EPSILON = 1e-4


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="ignore_cleanup_errors requires Python 3.10 or later",
)
def test_latlon():
    data = np.random.random((181, 360))

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        path = os.path.join(tmp, "a.grib")

        f = cml.new_grib_output(path, date=20010101)
        f.write(data, param="2t")
        f.close()

        ds = cml.load_source("file", path)
        print(ds[0])

        assert ds[0].metadata("date") == 20010101
        assert ds[0].metadata("param") == "2t"
        assert ds[0].metadata("levtype") == "sfc"
        assert ds[0].metadata("edition") == 2

        assert np.allclose(ds[0].to_numpy(), data, rtol=EPSILON, atol=EPSILON)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="ignore_cleanup_errors requires Python 3.10 or later",
)
def test_o96():
    data = np.random.random((40320,))

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        path = os.path.join(tmp, "a.grib")

        f = cml.new_grib_output(path, date=20010101)
        f.write(data, param="2t")
        f.close()

        ds = cml.load_source("file", path)

        assert ds[0].metadata("date") == 20010101
        assert ds[0].metadata("param") == "2t"
        assert ds[0].metadata("levtype") == "sfc"
        assert ds[0].metadata("edition") == 2

        assert np.allclose(ds[0].to_numpy(), data, rtol=EPSILON, atol=EPSILON)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="ignore_cleanup_errors requires Python 3.10 or later",
)
def test_o160():
    data = np.random.random((108160,))

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        path = os.path.join(tmp, "a.grib")

        f = cml.new_grib_output(path, date=20010101)
        f.write(data, param="2t")
        f.close()

        ds = cml.load_source("file", path)

        assert ds[0].metadata("date") == 20010101
        assert ds[0].metadata("edition") == 2
        assert ds[0].metadata("levtype") == "sfc"
        assert ds[0].metadata("param") == "2t"

        assert np.allclose(ds[0].to_numpy(), data, rtol=EPSILON, atol=EPSILON)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="ignore_cleanup_errors requires Python 3.10 or later",
)
def test_mars_labeling():
    data = np.random.random((40320,))

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        path = os.path.join(tmp, "a.grib")

        f = cml.new_grib_output(path, date=20010101)
        f.write(data, type="fc", expver="test", step=24, param="msl")
        f.close()

        ds = cml.load_source("file", path)

        assert ds[0].metadata("date") == 20010101
        assert ds[0].metadata("edition") == 2
        assert ds[0].metadata("step") == 24
        assert ds[0].metadata("expver") == "test"
        assert ds[0].metadata("levtype") == "sfc"
        assert ds[0].metadata("param") == "msl"
        assert ds[0].metadata("type") == "fc"

        assert np.allclose(ds[0].to_numpy(), data, rtol=EPSILON, atol=EPSILON)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="ignore_cleanup_errors requires Python 3.10 or later",
)
def test_pl():
    data = np.random.random((40320,))

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        path = os.path.join(tmp, "a.grib")

        f = cml.new_grib_output(path, date=20010101)
        f.write(data, param="t", level=850)
        f.close()

        ds = cml.load_source("file", path)

        assert ds[0].metadata("date") == 20010101
        assert ds[0].metadata("edition") == 2
        assert ds[0].metadata("level") == 850
        assert ds[0].metadata("levtype") == "pl"
        assert ds[0].metadata("param") == "t"

        assert np.allclose(ds[0].to_numpy(), data, rtol=EPSILON, atol=EPSILON)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="ignore_cleanup_errors requires Python 3.10 or later",
)
def test_tp():
    data = np.random.random((181, 360))

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        path = os.path.join(tmp, "a.grib")

        f = cml.new_grib_output(path, date=20010101)
        f.write(data, param="tp", step=48, edition=1)
        f.close()

        ds = cml.load_source("file", path)
        print(ds[0])

        assert ds[0].metadata("date") == 20010101
        assert ds[0].metadata("param") == "tp"
        assert ds[0].metadata("levtype") == "sfc"
        assert ds[0].metadata("edition") == 1
        assert ds[0].metadata("step") == 48

        assert np.allclose(ds[0].to_numpy(), data, rtol=EPSILON, atol=EPSILON)


if __name__ == "__main__":
    test_mars_labeling()
    # from climetlab.testing import main

    # main(__file__)
