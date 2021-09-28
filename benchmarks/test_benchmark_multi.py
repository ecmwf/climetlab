#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os

import pytest
import pytest_benchmark  # noqa: F401

from climetlab import load_source
from climetlab.core.temporary import temp_directory

LOG = logging.getLogger(__name__)


def large_multi_1(b, func):
    with temp_directory() as tmpdir:
        ilist = list(range(200))
        pattern = os.path.join(tmpdir, "test-{i}.nc")
        for i in ilist:
            source = load_source(
                "dummy-source",
                kind="netcdf",
                dims=["lat", "lon", "time"],
                coord_values=dict(time=[i + 0.0, i + 0.5]),
            )
            filename = pattern.format(i=i)
            source.save(filename)
        return b(func, pattern, ilist)


@pytest.mark.long_test
def test_large_multi_1_xarray(benchmark):
    import xarray as xr

    def func(pattern, ilist):
        return xr.open_mfdataset(
            pattern.format(i="*"), concat_dim="time", combine="nested"
        )

    large_multi_1(benchmark, func)


@pytest.mark.long_test
def test_large_multi_1_climetlab(benchmark):
    def func(pattern, ilist):
        source = load_source(
            "url-pattern",
            f"file://{pattern}",
            {"i": ilist},
            merger="concat(concat_dim=time)",
        )
        ds = source.to_xarray()
        return ds

    large_multi_1(benchmark, func)
