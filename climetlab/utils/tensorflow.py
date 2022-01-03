# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import keras
import tensorflow as tf

# https://github.com/tensorflow/docs/blob/304a7e4a90e53751ac59cab46667d78e81736fa3/site/en/guide/data_performance_analysis.md


def make_labels_hash_table(
    labels,
    name=None,
    key_dtype=None,
    dtype=tf.int64,
):

    if key_dtype is None:
        if all(isinstance(label, str) for label in labels):
            key_dtype = tf.string

        if all(isinstance(label, int) for label in labels):
            key_dtype = tf.int64

        if all(isinstance(label, float) for label in labels):
            key_dtype = tf.float64

    mapping = dict()
    for label in labels:
        mapping[len(mapping)] = label

    return mapping, tf.lookup.StaticHashTable(
        initializer=tf.lookup.KeyValueTensorInitializer(
            keys=tf.constant(labels, dtype=key_dtype),
            values=tf.constant(list(range(len(mapping))), dtype=dtype),
        ),
        default_value=tf.constant(-1, dtype=dtype),
        name=name,
    )


def make_label_one_hot(table, name=None, axis=-1):
    def wrapped(x):
        return tf.one_hot(
            table.lookup(x),
            int(table.size()),
            name=name,
            axis=axis,
        )

    return wrapped


class PeriodicConv2D(keras.layers.Conv2D):
    def call(self, inputs):
        w, h = self.kernel_size
        inputs = tf.concat([inputs, inputs[:, :, :w, :]], axis=2)
        inputs = tf.pad(
            inputs,
            [[0, 0], [h // 22, h // 2], [0, 0], [0, 0]],
            constant_values=0,
        )
        return super().call(inputs)
