#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import climetlab as cml
from climetlab import dataset, load_dataset
import os
import pytest


def test_dataset():
    load_dataset("sample-bufr-data")
    dataset.sample_bufr_data()


def test_datetime():
    if not os.path.exists(os.path.expanduser("~/.cdsapirc")):
        pytest.skip("No ~/.cdsapirc")

    data = cml.load_dataset(
        "era5-temperature", domain="france", period=(1980,), time=12
    )
    data["1980-12-09 12:00"]


def test_pandas_filter():
    data = cml.load_dataset("hurricane-database", "atlantic")
    irma = data.to_pandas(name="irma", year=2017)
    assert len(irma) == 66
