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

import pytest

import climetlab as cml
from climetlab.testing import modules_installed


@pytest.mark.skipif(
    not modules_installed("tensorflow"),
    reason="Tensorflow not installed",
)
def test_tfdataset_1():
    pass


@pytest.mark.skipif(
    not os.path.exists(os.path.expanduser("~/.cdsapirc")),
    reason="No ~/.cdsapirc",
)
@pytest.mark.skipif(
    not modules_installed("tensorflow"),
    reason="Tensorflow not installed",
)
def test_tfdataset_2():
    from tensorflow.keras.layers import Dense, Flatten, Input
    from tensorflow.keras.models import Sequential

    ds = cml.load_dataset("high-low")
    train, test = ds.to_tfdataset(split=["train", "test"])

    shape = train.element_spec[0].shape

    model = Sequential()
    model.add(Input(shape=(shape[-2], shape[-1])))
    model.add(Flatten())
    model.add(Dense(64, activation="sigmoid"))
    model.add(Dense(4, activation="softmax"))
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    print(model.summary())
    model.fit(train, epochs=1, verbose=0)
    model.evaluate(test)


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
