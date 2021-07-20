#!/usr/bin/env python3# (C) Copyright 2021 ECMWF.
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

import climetlab as cml
from climetlab.datasets import dataset_from_yaml
from climetlab.testing import MISSING

LOG = logging.getLogger(__name__)


def only_csv(path):
    return path.endswith(".csv")


def test_zenodo_1():

    ds = cml.load_source("zenodo", record_id=5020468, filter=only_csv)

    pd = ds.to_pandas()
    print(pd)
    assert len(pd) == 49


@pytest.mark.skipif(MISSING("tensorflow"), reason="Tensorflow not installed")
def test_zenodo_2():
    ds = cml.load_source(
        "zenodo",
        record_id=4707154,
        file_key="soltau_station_data.zip",
        filter="**/reforecasts_mx2t6_*.csv",
    )

    ds = ds.to_tfdataset()
    print(ds)


def test_zenodo_3():
    ds = cml.load_source(
        "zenodo",
        record_id=4707154,
        file_key="soltau_station_data.zip",
        filter="**/reforecasts_mx2t6_*.csv",
    )

    ds = ds.to_pandas()
    print(ds)


def test_zenodo_read_nc():
    def file_filter(path):
        return path.endswith("analysis_2t_2013-01-02.nc")

    ds = cml.load_source(
        "zenodo",
        record_id="4707154",
        file_key="europa_grid_data.zip",
        filter=file_filter,
        merger="concat(concat_dim=tt)",
    )
    ds = ds.to_xarray()
    assert "t2m" in list(ds.keys())


@pytest.mark.skipif(True, reason="Test not yet implemented")
def test_zenodo_read_nc_list_content():
    ds = cml.load_source("zenodo", record_id="3403963", list_only=True)

    with pytest.raises(NotImplementedError):
        ds = ds.to_xarray()

    content = ds.list_content_keys
    assert "2000_temperature_summary.nc" in content
    assert len(content) == 555


def test_zenodo_read_nc_partial():
    ds = cml.load_source(
        "zenodo",
        record_id="3403963",
        file_key="2000_temperature_summary.nc",
    )
    ds = ds.to_xarray()
    assert "t_min" in list(ds.keys())


@pytest.mark.skipif(True, reason="Test not yet implemented")
def test_zenodo_read_nc_partial_regexpr():
    ds = cml.load_source("zenodo", record_id="3403963", zenodo_file_filter="2000_.*.nc")
    ds = ds.to_xarray()
    assert "t_min" in list(ds.keys())


# def test_zenodo_merge():
#     an = cml.load_source(
#         "zenodo",
#         record_id="3403963",
#         zenodo_file_filter="analysis/2000_.*.nc",
#         merger=an_merger,
#     )
#     fc = cml.load_source(
#         "zenodo",
#         record_id="3403963",
#         zenodo_file_filter="forecast/2000_.*.nc",
#         merger=fc_merger,
#     )
#     ds = load_source("multi", an, fc, merger=an_with_fc)
#     ds.to_xarray()


def load_yaml(name, *args, **kwargs):
    full = os.path.join(os.path.dirname(__file__), name)
    return dataset_from_yaml(full, *args, **kwargs)


@pytest.mark.skipif(True, reason="Test not yet implemented")
def test_zenodo_from_yaml_1():
    s = load_yaml("zedono-dataset-1.yaml")
    s.to_pandas()


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
