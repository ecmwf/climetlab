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

import pytest

import climetlab as cml
from climetlab import dataset, load_dataset


def test_dataset_1():
    load_dataset("sample-bufr-data")


@pytest.mark.skipif(sys.version_info < (3, 7), reason="Version 3.7 or greater needed")
def test_dataset_2():
    dataset.sample_bufr_data()


def test_era5_temperature():
    if not os.path.exists(os.path.expanduser("~/.cdsapirc")):
        pytest.skip("No ~/.cdsapirc")

    cml.load_dataset("era5-temperature", period=(1979, 1982), domain="France", time=12)


def test_datetime():
    if not os.path.exists(os.path.expanduser("~/.cdsapirc")):
        pytest.skip("No ~/.cdsapirc")

    data = cml.load_dataset(
        "era5-temperature", domain="france", period=(1980,), time=12
    )
    data["1980-12-09 12:00"]
    with pytest.raises(NotImplementedError):
        data.sel(date="1980-12-09 12:00")


def test_pandas_filter():
    data = cml.load_dataset("hurricane-database", bassin="atlantic")
    irma = data.to_pandas(name="irma", year=2017)
    assert len(irma) == 66


if __name__ == "__main__":
    test_datetime()
