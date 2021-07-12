#!/usr/bin/env python3# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

import pytest

import climetlab as cml
from climetlab.datasets import dataset_from_yaml


def test_zenodo_read_csv():
    ds = cml.load_source(
        "zenodo",
        id="5020468",
    )
    ds = ds.to_pandas()
    assert len(ds) == 49


def test_zenodo_read_nc_with_merge():
    ds1 = cml.load_source("zenodo", id="654", filter="analysis.**")
    ds.merger = AnMerger

    ds2 = cml.load_source("zenodo", id="654", filter="forecast.**")
    ds.merger = FcMerger

    cml.load_source("multi", ds1, ds2, merger=AnFcMerger)


def test_zenodo_read_nc_2():
    ds = cml.load_source(
        "zenodo",
        record_id="4707154",
        filter=".*europa_grid_data.zip|europa_grid|.*analysis.*.nc",
    )
    print(ds)
    ds = ds.to_xarray()
    assert "t2m" in list(ds.keys())


def test_zenodo_read_nc():
    def file_filter(path):
        # return path.endswith('past_observations_2t_2009-01-02_4745.csv')
        return path.endswith("analysis_2t_2013-01-02.nc.nc")

    class ConcatMerger:
        def __init__(self, concat_dim="tt"):
            self.concat_dim = concat_dim

        def merge(self, paths, **kwargs):
            return xr.open_mfdataset(
                paths, concat_dim=self.concat_dim, combine="nested"
            )

    # ds = cml.load_source("zenodo", id="4707154", zenodo_file_filter = 'europa.*', file_filter = file_filter)
    # ds = ds.to_xarray()
    ds = cml.load_source(
        "zenodo",
        id="4707154",
        zenodo_file_filter="soltau.*",
        file_filter=file_filter,
        merger=ConcatMerger,
    )
    ds = ds.to_pandas()
    assert "t_min" in list(ds.keys())


def test_zenodo_read_nc_list_content():
    ds = cml.load_source("zenodo", id="3403963", list_only=True)

    with pytest.raises(NotImplementedError):
        ds = ds.to_xarray()

    content = ds.list_content_keys
    assert "2000_temperature_summary.nc" in content
    assert len(content) == 555


def test_zenodo_read_nc_partial():
    ds = cml.load_source(
        "zenodo", id="3403963", zenodo_file_filter=["2000_temperature_summary.nc"]
    )
    ds = ds.to_xarray()
    assert "t_min" in list(ds.keys())


def test_zenodo_read_nc_partial_regexpr():
    ds = cml.load_source("zenodo", id="3403963", zenodo_file_filter="2000_.*.nc")
    ds = ds.to_xarray()
    assert "t_min" in list(ds.keys())


def test_zenodo_merge():
    an = cml.load_source(
        "zenodo",
        id="3403963",
        zenodo_file_filter="analysis/2000_.*.nc",
        merger=an_merger,
    )
    fc = cml.load_source(
        "zenodo",
        id="3403963",
        zenodo_file_filter="forecast/2000_.*.nc",
        merger=fc_merger,
    )
    ds = load_source("multi", an, fc, merger=an_with_fc)
    ds.to_xarray()


# TODO: add zenodo test with tar.gz
# def test_zenodo_read_tar_gz():
#     ds = cml.load_source(
#         "zenodo",
#         id="4707154",
#     )
#     ds = ds.to_xarray()
#     print(ds)
#     assert "t" in ds.keys()


def load_yaml(name):
    full = os.path.join(os.path.dirname(__file__), name)
    return dataset_from_yaml(full)


def test_zenodo_from_yaml_1():
    s = load_yaml("zedono-dataset-1.yaml")
    s.to_pandas()


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
