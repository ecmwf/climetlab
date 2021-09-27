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

import pytest
import xarray as xr

from climetlab import load_source
from climetlab.core.temporary import temp_directory
from climetlab.testing import MISSING

LOG = logging.getLogger(__name__)


def large_multi_2_climetlab():
    import pandas as pd

    pattern = "https://storage.ecmwf.europeanweather.cloud/MAELSTROM_AP1/{parameter}_{size}/{date}T00Z.nc"

    dates = [
        i.strftime("%Y%m%d")
        for i in pd.date_range(start="2017-01-01", end="2017-12-31", freq="1D")
    ][:200]
    request = {"size": "5GB", "parameter": "air_temperature", "date": dates}

    s = load_source("url-pattern", pattern, request)
    return [t.path for t in s.sources]


def large_multi_2_xarray(paths):
    xr.open_mfdataset(paths, combine="nested", concat_dim="record")


@pytest.mark.long_test
@pytest.mark.external_download
@pytest.mark.skipif(
    MISSING("pytest_benchmark"), reason="pytest-benchmark not installed"
)
def test_large_multi_2_climetlab(benchmark):
    with temp_directory():
        large_multi_2_climetlab()
        benchmark(large_multi_2_climetlab)


@pytest.mark.long_test
@pytest.mark.external_download
@pytest.mark.skipif(
    MISSING("pytest_benchmark"), reason="pytest-benchmark not installed"
)
def test_large_multi_2_xarray(benchmark):

    with temp_directory():
        paths = large_multi_2_climetlab()
        benchmark(large_multi_2_xarray, paths)
