# flake8: noqa
import tensorflow as tf
from keras import backend as K
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Reshape
from tensorflow.keras.models import Sequential

import climetlab as cml

jobs = 10

print(K.get_session())

print("xxx", tf.config.threading.get_inter_op_parallelism_threads())
print("xxx", tf.config.threading.get_intra_op_parallelism_threads())

# tf.config.threading.set_inter_op_parallelism_threads(10)
# tf.config.threading.set_intra_op_parallelism_threads(10)

print("xxx", tf.config.threading.get_inter_op_parallelism_threads())
print("xxx", tf.config.threading.get_intra_op_parallelism_threads())

ds1 = cml.load_source("virtual", param="msl")
ds2 = cml.load_source("virtual", param="2t")

shape = ds1[0].shape
# https://stackoverflow.com/questions/47086599/parallelising-tf-data-dataset-from-generator


def dataset(ds):
    options = tf.data.Options()
    options.threading.private_threadpool_size = 10
    options.deterministic = False
    options.experimental_distribute.auto_shard_policy = tf.data.experimental.AutoShardPolicy.DATA

    return (
        ds.to_tfdataset()
        # .with_options(options)
        .batch(10240, num_parallel_calls=tf.data.AUTOTUNE)
        # .batch(1024, num_parallel_calls=10)
        # .batch(1024)
        .take(100)
        # .prefetch(10)
    )


tf1 = dataset(ds1)
tf2 = dataset(ds2)

print(shape)
# shape = tf1.element_spec.shape
# shape=(36,19)

model = Sequential()
model.add(Input(shape=(shape[-2], shape[-1])))
model.add(Flatten())
model.add(Dense(64, activation="sigmoid"))
model.add(Dense(64, activation="sigmoid"))
model.add(Dense(shape[-2] * shape[-1]))
model.add(Reshape(target_shape=(shape[-2], shape[-1])))

model.compile(
    optimizer="adam",
    loss="mean_squared_error",
    metrics=["mean_squared_error"],
)

input = tf.data.Dataset.zip((tf1, tf2))


print(model.summary())
model.fit(
    input,
    epochs=10,
    verbose=1,
    use_multiprocessing=True,
    workers=10,
)
