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
import sys

import numpy as np
import pytest

here = os.path.dirname(__file__)
sys.path.insert(0, here)
from indexing_fixtures import get_fixtures  # noqa: E402


@pytest.mark.parametrize("params", (["t", "u"], ["u", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
@pytest.mark.parametrize(
    "source_name",
    [
        "indexed-directory",
        # "list-of-dicts",
        # "file",
    ],
)
def test_indexing_to_xarray(params, levels, source_name):
    request = dict(level=levels, variable=params, date=20220929, time="1200")

    ds, __tmp, total, n = get_fixtures(source_name, {})

    ds = ds.sel(**request)
    ds = ds.order_by(level=levels, variable=params)
    assert len(ds) == n, len(ds)

    ds.to_xarray()


@pytest.mark.parametrize("params", (["u", "t"],))
@pytest.mark.parametrize("levels", ([1000, 850],))
@pytest.mark.parametrize(
    "source_name",
    [
        "indexed-directory",
        # "list-of-dicts",
        # "file",
    ],
)
def test_indexing_to_numpy(params, levels, source_name):
    request = dict(level=levels, variable=params, date=20220929, time="1200")

    ds, __tmp, total, n = get_fixtures(source_name, {})
    ds = ds.sel(**request)
    ds = ds.order_by(level=levels, variable=params)
    assert len(ds) == n, len(ds)

    print(ds[0].to_numpy().mean())
    print(ds[1].to_numpy().mean())
    print(ds[2].to_numpy().mean())
    print(ds[3].to_numpy().mean())

    assert np.abs(ds[0].to_numpy().mean() - 0.5083630135046184) < 10e-6
    assert np.abs(ds[1].to_numpy().mean() - 281.73044231454605) < 10e-6
    assert np.abs(ds[2].to_numpy().mean() - 1.9032698938640222) < 10e-6
    assert np.abs(ds[3].to_numpy().mean() - 274.671260493251) < 10e-6


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
