import climetlab as cml
import numpy as np
import tensorflow as tf

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

forecast = cml.load_source(
    # Build the request using: https://apps.ecmwf.int/mars-catalogue/
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

print("---------------------")
print("Constants:")
print(f"land_mask: {len(land_mask)}")
print()
# print("Number of DATES:", DATES)
# print("Number of TIMES:", TIMES)
print(f"forecast: {len(forecast)}")
print(f"era5: {len(era5)}")


print("")
forecast = forecast.order_by(date=None, time=None, param=None)
era5 = era5.order_by(date=None, time=None, param=None)


for i in forecast:
    print(i)
print(forecast.sel(param="z").statistics())
# print(forecast.sel(param="so").statistics())
print("")

for i in era5:
    print(i)
print(era5.statistics())
print("")

for i in range(0, len(era5)):
    print(f"--- Sample {i} -----")
    print(forecast[i])
    #    print(forecast[i * 2])
    print(era5[i])
shape = era5[1].to_numpy().shape


# tfds_era5 = era5.to_tfdataset()
# tfds = forecast.to_tfdataset(targets=tfds_era5)

# tfds = forecast.to_tfdataset(targets=era5)
print("-----------")

forecast.statistics()


from climetlab.readers.grib.tensorflow import (
    to_tf_func,
    default_merger,
    cml_tfzip,
    global_to_tfdataset,
)

total_size = len(forecast)
prefetch = 10

indices = tf.data.Dataset.range(total_size)
indices = indices.shuffle(100)  # shuffle can happen early

datasets = [forecast, era5, land_mask]


print(datasets)
mode = 6
if mode == 1:  # works ok
    datasets = [ds._to_numpy_func() for ds in datasets]
    features = [datasets[0], datasets[0]]  # need to add custom merge and broadcasting
    targets = [datasets[1], datasets[1]]
    features_func, n_features = merge_funcs(*features)
    targets_func, n_targets = merge_funcs(*targets)
    features_tfds = indices.map(to_tf_func(features_func))
    targets_tfds = indices.map(to_tf_func(targets_func))

elif mode == 2:  # works ok
    datasets = [ds._to_tfdataset(indices) for ds in datasets]
    features = [datasets[0], datasets[2]]
    targets = [datasets[1]]
    features_tfds, n_features = merge_cached_numpy_funcs(
        *features, indices=indices, merger=default_merger
    )
    targets_tfds, n_targets = merge_cached_numpy_funcs(*targets, indices=indices)

elif mode == 3:
    features_tfds = datasets[0].to_tfdataset_(datasets[2])
    targets_tfds = datasets[1].to_tfdataset_(datasets[1], align_with=features_tfds)
    n_features = features_tfds._climetlab_n
    n_targets = targets_tfds._climetlab_n

    shape_in = features_tfds._climetlab_tf_shape
    shape_out = targets_tfds._climetlab_tf_shape
    tfds = cml_tfzip(features_tfds, targets_tfds)

elif mode == 5:
    tfds = global_to_tfdataset(
        [datasets[0], datasets[2]],
        [datasets[1]],
    )
    shape_in = (2, 19, 36)  # tfds._climetlab_tf_shape
    shape_out = (1, 19, 36)  # tfds._climetlab_tf_shape
elif mode == 6:
    tfds = datasets[0].to_tfdataset(
        datasets[2],
        targets=[datasets[1]],
        options=[dict(), dict(constant=True)],
        targets_options=[],
    )
    shape_in = (2, 19, 36)  # tfds._climetlab_tf_shape
    shape_out = (1, 19, 36)  # tfds._climetlab_tf_shape

# elif mode==0: # not implemented
#     datasets = [ds._to_tf_func() for ds in datasets]
#     features = [datasets[0], datasets[0]] # need to add custom merge and broadcasting
#     targets = [datasets[1],datasets[1]]
#     features_tf_func, n_features = merge_tf_funcs(*features)
#     targets_tf_func, n_targets = merge_tf_funcs(*targets)
#     features_tfds = indices.map(features_tf_func)
#     targets_tfds = indices.map(targets_tf_func)
#
# elif mode==-1: # not implemented
#     datasets = [ds._to_tfdataset(indices) for ds in datasets]
#     features = [datasets[0], datasets[0]] # need to add custom merge and broadcasting
#     targets = [datasets[1],datasets[1]]
#     features_tfds, n_features = merge_tfdatasets(*features)
#     targets_tfds, n_targets = merge_tfdatasets(*targets)


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
# features_tfds = features_tfds.prefetch(prefetch)
model.fit(tfds)
