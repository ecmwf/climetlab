# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

LOG = logging.getLogger(__name__)


class TensorflowMixIn:
    def to_tfdataset(
        self,
        labels=None,
        num_parallel_calls=10,
        prefetch=1024,
        **kwargs,
    ):

        import tensorflow as tf

        def map_fn(i):
            i = int(i)
            return self[i].to_numpy()

        @tf.function
        def tf_map_fn(i):
            return tf.py_function(func=map_fn, inp=[i], Tout=tf.float32)

        def map_label_fn(i):
            i = int(i)
            return labels(i)

        @tf.function
        def tf_map_label_fn(i):
            return tf.py_function(func=map_label_fn, inp=[i], Tout=tf.float32)

        def dataset(mapping):
            return (
                tf.data.Dataset.range(len(self))
                .map(mapping, num_parallel_calls=num_parallel_calls)
                .prefetch(prefetch)
            )

        if labels is None:
            return dataset(tf_map_fn)

        return tf.data.Dataset.zip(
            (
                dataset(tf_map_fn),
                dataset(tf_map_label_fn),
            )
        )
