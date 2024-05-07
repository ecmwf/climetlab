import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Reshape
from tensorflow.keras.models import Sequential

import climetlab as cml

param = "msl"
t2m = cml.load_source(
    "cds",
    "reanalysis-era5-single-levels",
    variable=param,
    product_type="reanalysis",
    date="2011-01-01/to/2012-12-31",
    grid=[5.625, 5.625],
    time=list(range(0, 24)),
)

t2m_val = cml.load_source(
    "cds",
    "reanalysis-era5-single-levels",
    variable=param,
    product_type="reanalysis",
    date="2013-01-01/to/2013-12-31",
    grid=[5.625, 5.625],
    time=list(range(0, 24)),
)


class PeriodicConv2D(Conv2D):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.kernel_size)

    def call(self, inputs):
        w, h = self.kernel_size
        inputs = tf.concat([inputs, inputs[:, :, :w, :]], axis=2)
        inputs = tf.pad(inputs, [[0, 0], [h // 2, h // 2], [0, 0], [0, 0]], constant_values=0)
        return super().call(inputs)


print(t2m.statistics())
mu = t2m.statistics()["average"]
ro = t2m.statistics()["stdev"]


def normalize(x, y):
    return (x - mu) / ro, (y - mu) / ro


def prepare(dataset):
    print(dataset)
    dataset = dataset.shuffle(1024)
    dataset = dataset.batch(365)
    dataset = dataset.apply(lambda ds: ds.map(normalize))
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    return dataset


dataset = prepare(t2m.to_tfdataset(offset=3 * 24))

validation = prepare(t2m_val.to_tfdataset(offset=3 * 24))


# for n in dataset.take(1):
#     print(n)


shape = dataset.element_spec[0].shape

print(shape)


class MyModel(Sequential):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.foo = 42


model = MyModel(name=f"{param}_{ro}_{mu}")
model.add(Input(shape=(shape[-2], shape[-1])))
model.add(Reshape((shape[-2], shape[-1], 1), name="add_depth"))
for n in range(1):
    model.add(Conv2D(64, kernel_size=(3, 3), activation="relu"))
    model.add(Dropout(0.5))
model.add(Flatten())
model.add(Dense(shape[-2] * shape[-1]))
model.add(Reshape(target_shape=(shape[-2], shape[-1]), name="result"))


model.summary()
batch_size = 128
epochs = 1

model.compile(
    loss="mse",
    optimizer="adam",
    metrics=["mse"],
)

model.fit(
    dataset,
    batch_size=batch_size,
    epochs=epochs,
    callbacks=[
        EarlyStopping(
            # monitor="loss",
            patience=4,
            restore_best_weights=True,
        ),
        # TensorBoard(
        #     log_dir="logs",
        #     histogram_freq=1,
        #     # profile_batch="500,520",
        #     profile_batch=(1, 1000),
        # ),
    ],
    validation_data=validation,
)

model.save("my_model.h5")


results = model.evaluate(validation)
print(results)
