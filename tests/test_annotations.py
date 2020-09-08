#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import numpy as np
import pandas as pd
import xarray as xr

from climetlab.core.metadata import annotate, annotation


class Owner:
    pass


def test_pandas_annotations():
    data = dict(a=["foo", "bar"], b=[1, 2])

    df1 = pd.DataFrame(data, columns=["a", "b"])

    obj1 = Owner()
    assert annotate(df1, obj1, foo=42) is df1
    assert "climetlab-0" in df1._metadata

    a1 = annotation(df1)

    assert a1.get("foo") == 42
    assert a1.owner is obj1

    df2 = df1[df1.b == 42]
    a2 = annotation(df2)
    assert a2.get("foo") == 42
    assert a2.owner is obj1

    assert a1 is a2

    del obj1

    assert a2.owner is None

    obj3 = Owner
    df3 = pd.DataFrame(data, columns=["a", "b"])
    annotate(df3, obj3, bar=42)

    a3 = annotation(df3)
    assert a1 is not a3

    assert "climetlab-0" in df3._metadata


def test_xarray_annotations():

    # Examples from xarray documentation

    # Data array
    ############

    data = np.random.rand(4, 3)
    locs = ["IA", "IL", "IN"]
    times = pd.date_range("2000-01-01", periods=4)
    xr1 = xr.DataArray(data, coords=[times, locs], dims=["time", "space"])
    obj1 = Owner()
    assert annotate(xr1, obj1, foo=42) is xr1

    a1 = annotation(xr1)
    assert a1.get("foo") == 42

    # Dataset
    #########

    temp = 15 + 8 * np.random.randn(2, 2, 3)
    precip = 10 * np.random.rand(2, 2, 3)
    lon = [[-99.83, -99.32], [-99.79, -99.23]]
    lat = [[42.25, 42.21], [42.63, 42.59]]

    xr2 = xr.Dataset(
        {
            "temperature": (["x", "y", "time"], temp),
            "precipitation": (["x", "y", "time"], precip),
        },
        coords={
            "lon": (["x", "y"], lon),
            "lat": (["x", "y"], lat),
            "time": pd.date_range("2014-09-06", periods=3),
            "reference_time": pd.Timestamp("2014-09-05"),
        },
    )

    annotate(xr2, obj1, bar=42)
    a1 = annotation(xr2)
    assert a1.get("bar") == 42

    # Dataset from Data array
    # annotation must be preserved

    # xr3 = xr1.to_dataset(name="test")
    # a3 = annotation(xr3)
    # assert a3.get("foo") == 42
