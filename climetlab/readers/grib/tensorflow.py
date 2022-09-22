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


def to_tfdataset(
    features,
    targets=None,
    total_size=None,
    num_parallel_calls=10,
    prefetch=1024,
    **kwargs,
):

    import tensorflow as tf

    if features is not None and not callable(features):
        if total_size is None:
            LOG.debug("No total_size specified, infering from features.")
            total_size = len(features)

        _features = features

        def features(i):
            return _features[i].to_numpy()

    if targets is not None and not callable(targets):
        _targets = targets

        def targets(i):
            return _targets[i].to_numpy()

    assert total_size is not None

    def map_fn(i):
        i = int(i)
        return features(i)

    @tf.function
    def tf_map_fn(i):
        return tf.py_function(func=map_fn, inp=[i], Tout=tf.float32)

    def map_label_fn(i):
        i = int(i)
        return targets(i)

    @tf.function
    def tf_map_label_fn(i):
        return tf.py_function(func=map_label_fn, inp=[i], Tout=tf.float32)

    def dataset(mapping):
        return (
            tf.data.Dataset.range(total_size)
            .map(mapping, num_parallel_calls=num_parallel_calls)
            .prefetch(prefetch)
        )

    if targets is None:
        return dataset(tf_map_fn)

    return tf.data.Dataset.zip(
        (
            dataset(tf_map_fn),
            dataset(tf_map_label_fn),
        )
    )


class TensorflowMixIn:
    def to_tfdataset(
        self,
        labels=None,
        targets=None,
        **kwargs,
    ):
        if targets is None:  # rename "labels" into "targets" ?
            targets = labels
        return to_tfdataset(features=self, targets=targets, **kwargs)
