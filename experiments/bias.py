a = 0
print("loading cml")
import climetlab as cml

print("cml loaded")

import numpy as np

print("loading tf")
import tensorflow as tf

print("loading tf")

# land_mask = cml.load_source( "mars", param="lsm", levtype="sfc", expver = "1", date = "2020-01-01", stream = "oper", grid = GRID, type = "an", time = "00:00:00" ,)

## topo = cml.load_source( "mars", param="129.128", levtype="sfc", expver = "1", date = "2019-05-01", stream = "oper", grid = "2/2", type = "an", time = "00:00:00")
# TODO: check with Mariana: 129.128 is geopotential not topo.
# topo = cml.load_source( "mars", param="topo", levtype="sfc", expver = "1", date = "2019-05-01", stream = "oper", grid = "2/2", type = "an", time = "00:00:00")


GRID = "10/10"
DATES = "2022-09-02/to/2022-09-04"
TIMES = ["00:00:00", "12:00:00"]
# TIMES= dict(time=[0,12]) # should work

land_mask = cml.load_source(
    "mars",
    param="lsm",
    levtype="sfc",
    expver="1",
    stream="oper",
    type="an",
    time="00:00:00",
    date="2022-09-30",
    grid=GRID,
)

# Build the request using: https://apps.ecmwf.int/mars-catalogue/
forecast = cml.load_source(
    "mars",
    **{"class": "od"},
    stream="oper",
    date=DATES,
    expver="1",
    levtype="sfc",
    param=["z"],
    # param=["t", "z"],  # z geopotential=129, t temperature = "130.128"
    step=24,
    time=TIMES,
    type="fc",
    grid=GRID,
)


era5 = cml.load_source(
    # Build request using: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=form
    "cds",
    "reanalysis-era5-single-levels",
    product_type="reanalysis",
    time=TIMES,
    param="2t",
    grid=GRID,
    date=DATES,
    format="grib",
)
# era5 = cml.load_source(
#    "mars",
#    **{"class": "ea"},
#    date=DATES,
#    expver="1",
#    levtype="sfc",
#    param="2t",
#    stream="oper",
#    time=TIMES,
#    type="an",
#    # levelist="850",
#    grid=GRID,
# )
forecast = forecast.order_by("date", "time", "param")
era5 = era5.order_by("date", "time", "param")

print("---------------------")
print("Constants:")
print(f"land_mask: {len(land_mask)}")
print()
# print("Number of DATES:", DATES)
# print("Number of TIMES:", TIMES)
print(f"forecast: {len(forecast)}")
print(f"era5: {len(era5)}")
print("")

for i, (x, y) in enumerate(zip(forecast, era5)):
    print(f"--- Sample {i} -----")
    print(x)
    print(y)
print("")


for i in range(0, len(era5)):
    print(f"--- Sample {i} -----")
    print(forecast[i])
    #    print(forecast[i * 2])
    print(era5[i])
shape = era5[1].to_numpy().shape

print("-----------")

forecast.statistics()

datasets = [forecast, era5, land_mask]

print(datasets)
tfds = datasets[0].to_tfdataset(
    datasets[0], datasets[2],
    targets=[datasets[1]],
    options=[
        dict(normalize="mean-std"),
        dict(normalize="mean-std"),
        dict(normalize="mean-std", constant=True),
    ],
    targets_options=[
        dict(normalize="min-max"),
    ],
)
shape_in = tfds._climetlab_tf_shape_in
shape_out = tfds._climetlab_tf_shape_out
assert shape_in == (3, 19, 36)
assert shape_out == (1, 19, 36)


def build_model(shape_in, shape_out):

    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import (
        Dense,
        Flatten,
        Input,
        Reshape,
    )

    model = Sequential(name="ML_model")
    model.add(Input(shape=(shape_in[-3], shape_in[-2], shape_in[-1])))
    model.add(Flatten())
    model.add(Dense(shape_out[-3] * shape_out[-2] * shape_out[-1]))
    model.add(
        Reshape(
            target_shape=(shape_out[-3], shape_out[-2], shape_out[-1]), name="output"
        )
    )

    model.summary()

    model.compile(
        loss="mse",
        optimizer="adam",
    )

    return model


model = build_model(shape_in, shape_out)
model.fit(tfds)

print("===========")
for i, j in tfds:
    import climetlab.prompt
    pred = model.predict(i)
    out = j + pred
    print(out.shape)

import climetlab.prompt
