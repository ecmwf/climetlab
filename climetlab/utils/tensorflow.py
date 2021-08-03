# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import tensorflow as tf  # noqa


def python_dict_to_tensorflow_hash_table(labels, name=None, dtype=tf.int32):

    assert False, "Work in progress"

    mapping = dict()
    for label in labels:
        mapping[len(mapping)] = label

    return tf.lookup.StaticHashTable(
        initializer=tf.lookup.KeyValueTensorInitializer(
            keys=tf.constant(mapping, dtype=dtype),
            values=tf.constant(list(range(len(mapping))), dtype=dtype),
        ),
        default_value=tf.constant(-1, dtype=dtype),
        name=name,
    )


def make_label_one_hot(table, name=None, axis=-1):
    def wrapped(x):
        return tf.one_hot(table.lookup(x), len(table), name=name, axis=axis)

    return wrapped
