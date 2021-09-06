# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, TensorBoard
from tensorflow.keras.layers import (  # AveragePooling2D,; Conv2D,; Reshape,
    Dense,
    Flatten,
    InputLayer,
)
from tensorflow.keras.models import Sequential

from climetlab import load_source
from climetlab.utils.tensorflow import make_label_one_hot, make_labels_hash_table

# years = list(range(1979, 1979 + 4))
years = list(range(1979, 2021))
# years = list(range(1979, 1979 + 1))

PARAMS = (
    129,
    134,
    136,
    137,
    139,
    140121,
    140122,
    140123,
    140124,
    140125,
    140126,
    140127,
    140128,
    140129,
    140207,
    140208,
    140209,
    140211,
    140212,
    140214,
    140215,
    140216,
    140217,
    140218,
    140219,
    140220,
    140221,
    140222,
    140223,
    140224,
    140225,
    140226,
    140227,
    140228,
    140229,
    140230,
    140231,
    140232,
    140233,
    140234,
    140235,
    140236,
    140237,
    140238,
    140239,
    140244,
    140245,
    140249,
    140252,
    140253,
    140254,
    141,
    142,
    143,
    144,
    145,
    146,
    147,
    148,
    15,
    151,
    159,
    16,
    160,
    161,
    162,
    162053,
    162054,
    162059,
    162060,
    162061,
    162062,
    162063,
    162064,
    162065,
    162066,
    162067,
    162068,
    162069,
    162070,
    162071,
    162072,
    162073,
    162074,
    162075,
    162076,
    162077,
    162078,
    162079,
    162080,
    162081,
    162082,
    162083,
    162084,
    162085,
    162086,
    162087,
    162088,
    162089,
    162090,
    162091,
    162092,
    163,
    164,
    165,
    166,
    167,
    168,
    169,
    17,
    170,
    172,
    175,
    176,
    177,
    178,
    179,
    18,
    180,
    181,
    182,
    183,
    186,
    187,
    188,
    195,
    196,
    197,
    198,
    205,
    206,
    207,
    208,
    209,
    210,
    211,
    212,
    213,
    228,
    228001,
    228003,
    228007,
    228008,
    228009,
    228010,
    228011,
    228012,
    228013,
    228014,
    228015,
    228016,
    228017,
    228018,
    228019,
    228021,
    228022,
    228023,
    228024,
    228029,
    228088,
    228089,
    228090,
    228129,
    228130,
    228131,
    228132,
    228217,
    228218,
    228219,
    228220,
    228221,
    228246,
    228247,
    228251,
    229,
    230,
    231,
    232,
    235,
    235020,
    235021,
    235023,
    235024,
    235025,
    235026,
    235027,
    235029,
    235030,
    235031,
    235032,
    235033,
    235034,
    235035,
    235036,
    235037,
    235038,
    235039,
    235040,
    235041,
    235042,
    235043,
    235045,
    235046,
    235047,
    235048,
    235049,
    235050,
    235051,
    235052,
    235053,
    235054,
    235055,
    235056,
    235057,
    235058,
    235059,
    235068,
    235069,
    235070,
    236,
    238,
    239,
    240,
    243,
    244,
    245,
    26,
    260015,
    260121,
    260123,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    48,
    50,
    57,
    59,
    66,
    67,
    74,
    78,
    79,
    8,
    9,
)

s = load_source(
    "cds",
    "reanalysis-era5-single-levels-monthly-means",
    variable="all",
    year=years,
    month=list(range(1, 13)),
    time=0,
    product_type="monthly_averaged_reanalysis",
    # grid=[0.25, 0.25],
    grid=[1, 1],
    split_on="year",
)


dataset = s.to_tfdataset(label="paramId")

mapping, table = make_labels_hash_table(PARAMS)
one_hot_1 = make_label_one_hot(table, "paramId")


def one_hot(data, paramId):
    return data, one_hot_1(paramId)


# print(dataset.element_spec)
dataset = dataset.shuffle(1024)
dataset = dataset.map(one_hot)

dataset = dataset.batch(len(mapping) * 10)
# dataset = dataset.batch(1)

dataset = dataset.prefetch(tf.data.AUTOTUNE)


for n in dataset.take(1):
    print(n)

shape = dataset.element_spec[0].shape
print(shape)


model = Sequential()
model.add(InputLayer(input_shape=(shape[-2], shape[-1])))


model.add(Flatten())
model.add(Dense(2, activation="relu"))
model.add(Dense(len(mapping), activation="softmax"))
print(model.summary())


model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

print(model.summary())

split = 1
print(split)
validation = dataset.take(split)
train = dataset.skip(split)


model.fit(
    train,
    epochs=2,
    verbose=1,
    validation_data=validation,
    callbacks=[
        EarlyStopping(
            # monitor="val_accuracy",
            patience=10,
        ),
        TensorBoard(
            log_dir="logs",
            histogram_freq=1,
            # profile_batch="500,520",
            profile_batch=(1, 1000),
        ),
    ],
)

print(len(s))
