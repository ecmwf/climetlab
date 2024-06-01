# flake8: noqa
a = 0
print("loading cml")
import climetlab as cml

print("cml loaded")

import numpy as np
from mydatasets.bias_test import BiasTest

from climetlab.utils.dates import to_datetime_list

# land_mask = cml.load_source( "mars", param="lsm", levtype="sfc", expver = "1", date = "2020-01-01", stream = "oper", grid = GRID, type = "an", time = "00:00:00" ,)

## topo = cml.load_source( "mars", param="129.128", levtype="sfc", expver = "1", date = "2019-05-01", stream = "oper", grid = "2/2", type = "an", time = "00:00:00")
# TODO: check with Mariana: 129.128 is geopotential not topo.
# topo = cml.load_source( "mars", param="topo", levtype="sfc", expver = "1", date = "2019-05-01", stream = "oper", grid = "2/2", type = "an", time = "00:00:00")


forecast = cml.load_dataset("bias-test", "forecast", param="2t")
era5 = cml.load_dataset("bias-test", "era5", param="2t")
land_mask = cml.load_dataset("bias-test", "constant")

print("---------------------")
print("Constants:")
print(f"land_mask: {len(land_mask)}")
print()
# print("Number of DATES:", DATES)
# print("Number of TIMES:", TIMES)
print(f"forecast: {len(forecast)}")
print(f"era5: {len(era5)}")
print("")

print(era5.availability)

# for i in range(0, len(forecast)):
for i in [0, 1, 2, len(forecast) - 2, len(forecast) - 1]:
    print(f"--- Sample {i} -----")
    print("fcast=", forecast[i])
    print("era5 =", era5[i])
print("")

assert len(era5) == len(forecast)
shape = era5[1].to_numpy().shape

print("-----------")

forecast.statistics()

datasets = [forecast, era5, land_mask]

print("loading tf")
import tensorflow as tf

print("loaded tf")

print(datasets)
tfds = datasets[0].to_tfdataset2(
    features=[datasets[0], datasets[2]],  # default to [self] is missing
    targets=[datasets[1]],
    options=[
        dict(normalize="mean-std"),
        dict(normalize="mean-std", constant=True),
    ],
    targets_options=[
        dict(normalize="min-max"),
    ],
)
shape_in = tfds._climetlab_tf_shape_in
shape_out = tfds._climetlab_tf_shape_out
assert shape_in == (2, 91, 180), shape_in
assert shape_out == (1, 91, 180), shape_out


def build_model(shape_in, shape_out):
    from tensorflow.keras.layers import Dense
    from tensorflow.keras.layers import Flatten
    from tensorflow.keras.layers import Input
    from tensorflow.keras.layers import Reshape
    from tensorflow.keras.models import Sequential

    model = Sequential(name="ML_model")
    model.add(Input(shape=(shape_in[-3], shape_in[-2], shape_in[-1])))
    model.add(Flatten())
    model.add(Dense(shape_out[-3] * shape_out[-2] * shape_out[-1]))
    model.add(Reshape(target_shape=(shape_out[-3], shape_out[-2], shape_out[-1]), name="output"))

    model.summary()

    model.compile(
        loss="mse",
        optimizer="adam",
    )

    return model


model = build_model(shape_in, shape_out)
model.fit(tfds)

print("===========")
# TODO: predict
