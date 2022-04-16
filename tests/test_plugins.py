#!/usr/bin/env python3

# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import numpy as np

import climetlab as cml
from climetlab.datasets import Dataset
from climetlab.datasets import register as register_dataset
from climetlab.sources import Source
from climetlab.sources import register as register_source


class RegisteredSource(Source):
    def __init__(self, shape):
        self.shape = shape

    def to_numpy(self):
        return np.zeros(self.shape)


def test_register_source():
    register_source("test-register-source", RegisteredSource)
    ds = cml.load_source("test-register-source", shape=(3, 3))

    assert ds.to_numpy().shape == (3, 3)


class RegisteredDataset(Dataset):
    def __init__(self, shape):
        self.shape = shape

    def to_numpy(self):
        return np.zeros(self.shape)


def test_register_dataset():
    register_dataset("test-register-dataset", RegisteredDataset)
    ds = cml.load_dataset("test-register-dataset", shape=(3, 3))
    assert ds.to_numpy().shape == (3, 3)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
