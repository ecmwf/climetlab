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
from climetlab import dataset
from climetlab import load_dataset
from climetlab.testing import NO_CDS


def test_dataset_1():
    load_dataset("sample-bufr-data")


def test_dataset_2():
    dataset.sample_bufr_data()


@pytest.mark.long_test
@pytest.mark.download
@pytest.mark.skipif(NO_CDS, reason="No access to CDS")
def test_era5_temperature():
    cml.load_dataset("era5-temperature", period=(1979, 1982), domain="France", time=12)


@pytest.mark.long_test
@pytest.mark.download
@pytest.mark.skipif(NO_CDS, reason="No access to CDS")
def test_datetime():
    data = cml.load_dataset("era5-temperature", domain="france", period=(1980,), time=12)
    data["1980-12-09 12:00"]
    with pytest.raises(ValueError):
        data.sel(date="1980-12-09 12:00")


@pytest.mark.external_download
@pytest.mark.download
@pytest.mark.skipif(True, reason="hurricane database changed")
def test_pandas_filter():
    data = cml.load_dataset("hurricane-database", bassin="atlantic")
    irma = data.to_pandas(name="irma", year=2017)
    assert len(irma) == 66


def test_unknown_dataset():
    with pytest.raises(NameError):
        load_dataset("do-not-exist-lkj45a45qsdf3")


@pytest.mark.download
def test_remote_dataset_from_climetlab_catalog():
    load_dataset("sample-netcdf-data")


@pytest.mark.download
def test_samples():
    cml.load_dataset("meteonet-samples-radar")


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
