# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import warnings
from itertools import zip_longest
from numbers import Number

import numpy as np

from climetlab.core import Base

LOG = logging.getLogger(__name__)


# def to_tfdataset(
#     features,
#     targets=None,
#     total_size=None,
#     num_parallel_calls=10,
#     prefetch=1024,
#     **kwargs,
# ):
#
#     import tensorflow as tf
#
#     if features is not None and not callable(features):
#         if total_size is None:
#             LOG.debug("No total_size specified, infering from features.")
#             total_size = len(features)
#
#         _features = features
#
#         def features(i):
#             return _features[i].to_numpy()
#
#     if targets is not None and not callable(targets):
#         _targets = targets
#
#         def targets(i):
#             return _targets[i].to_numpy()
#
#     assert total_size is not None
#
#     def map_fn(i):
#         i = int(i)
#         return features(i)
#
#     @tf.function
#     def tf_map_fn(i):
#         return tf.py_function(func=map_fn, inp=[i], Tout=tf.float32)
#
#     def map_label_fn(i):
#         i = int(i)
#         return targets(i)
#
#     @tf.function
#     def tf_map_label_fn(i):
#         return tf.py_function(func=map_label_fn, inp=[i], Tout=tf.float32)
#
#     def dataset(mapping):
#         return (
#             tf.data.Dataset.range(total_size)
#             .map(mapping, num_parallel_calls=num_parallel_calls)
#             .prefetch(prefetch)
#         )
#
#     if targets is None:
#         return dataset(tf_map_fn)
#
#     return tf.data.Dataset.zip(
#         (
#             dataset(tf_map_fn),
#             dataset(tf_map_label_fn),
#         )
#     )


def default_merger(*funcs):
    # old: moved to climetlab.ml
    if not funcs:
        return None

    def map_fn(i):
        i = int(i)
        arrays = [m(i) for m in funcs]
        array = np.stack(arrays)
        return array

    return map_fn


def as_numpy_func(ds, options=None):
    # old: moved to climetlab.ml
    if ds is None or callable(ds):
        return ds

    def _options(new):
        o = {k: v for k, v in ds.get_options().items()}
        if new:
            o.update(new)
        return o

    options = _options(options)

    to_numpy_kwargs = options.get("to_numpy_kwargs", {})

    def take_i(i):
        return ds[i].to_numpy(**to_numpy_kwargs)

    if "offset" in options and options["offset"]:
        offset = options["offset"]

        def take_i(i):  # noqa: F811
            return ds[i + offset].to_numpy(**to_numpy_kwargs)

    func = take_i

    if "constant" in options and options["constant"]:

        def first(func):
            def wrap(i):
                return func(0)

            return wrap

        func = first(func)

    if "normalize" in options:
        a, b = normalize_a_b(options["normalize"], ds)

        def normalize(func):
            def wrap(i):
                return a * func(i) + b

            return wrap

        func = normalize(func)

    return func


def normalize_a_b(option, dataset):
    if isinstance(option, (tuple, list)) and all(
        [isinstance(x, Number) for x in option]
    ):
        a, b = option
        return a, b

    if option == "mean-std":
        stats = dataset.statistics()
        average, stdev = stats["average"], stats["stdev"]
        if stdev < (average * 1e-6):
            warnings.warn(
                f"Normalizing: the field seems to have only one value {stats}"
            )
        return 1 / stdev, -average / stdev

    if option == "min-max":
        stats = dataset.statistics()
        mini, maxi = stats["minimum"], stats["maximum"]
        x = maxi - mini
        if x < 1e-9:
            warnings.warn(
                f"Normalizing: the field seems to have only one value {stats}."
            )
        return 1 / x, -mini / x

    raise ValueError(option)


def to_funcs(features, targets, options, targets_options, merger, targets_merger):
    if targets is None:
        targets = []

    if options is None:
        options = [{} for i in features]

    if targets_options is None:
        targets_options = [{} for i in targets]

    assert isinstance(features, (list, tuple)), features
    assert len(features) == len(options), (len(features), len(options))
    funcs = [
        as_numpy_func(_, opt) for _, opt in zip_longest(features, options, fillvalue={})
    ]
    funcs_targets = [
        as_numpy_func(_, opt)
        for _, opt in zip_longest(targets, targets_options, fillvalue={})
    ]

    func = merger(*funcs)
    func_targets = targets_merger(*funcs_targets)

    return func, func_targets


def to_tfdataset2(
    total_size=None,
    features=None,
    targets=None,
    options=None,
    targets_options=None,
    merger=default_merger,
    targets_merger=default_merger,
    #
    num_parallel_calls=10,
    prefetch=1024,
    shuffle_buffer_size=100,
    **kwargs,
):
    if total_size is None:
        total_size = len(features[0])

    import tensorflow as tf

    func, func_targets = to_funcs(
        features, targets, options, targets_options, merger, targets_merger
    )

    indices = tf.data.Dataset.range(total_size)
    if shuffle_buffer_size:
        indices = indices.shuffle(shuffle_buffer_size)

    def dataset(f):
        def map_fn(i):
            i = int(i)
            return f(i)

        @tf.function  # only for debugging
        def tf_map_fn(i):
            return tf.py_function(func=map_fn, inp=[i], Tout=tf.float32)

        ds = indices.map(tf_map_fn, num_parallel_calls=num_parallel_calls)
        ds = ds.prefetch(prefetch)
        return ds

    if func_targets is None:
        tfds = dataset(func)
        tfds._climetlab_shape = func(0).shape
        return tfds

    tf_features = dataset(func)
    tf_targets = dataset(func_targets)
    tfds = tf.data.Dataset.zip((tf_features, tf_targets))

    # TODO: use metadata from grib directly, without loading the numpy array
    tfds._climetlab_tf_shape_in = func(0).shape

    if targets:
        tfds._climetlab_tf_shape_out = func_targets(0).shape

    tfds._climetlab_tf_input = tf_features
    if targets:
        tfds._climetlab_tf_targets = tf_targets
    # ds = ds.prefetch(prefetch)

    return tfds


class NumpyFuncWrapper:
    __slots__ = ["_wrapped_ds", "_wrapped_opt"]

    def __init__(self, ds, opt={}):
        self.__class__._wrapped_ds.__set__(self, ds)
        self.__class__._wrapped_opt.__set__(self, opt)

    def __getattr__(self, name):
        return getattr(self._wrapped_ds, name)

    def __setattr__(self, name, value):
        return setattr(self._wrapped_ds, name, value)


class TensorflowMixIn:
    # def to_tfdataset(
    #     self,
    #     labels=None,
    #     targets=None,
    #     **kwargs,
    # ):
    #     if targets is None:  # rename "labels" into "targets" ?
    #         targets = labels
    #     return to_tfdataset(features=self, targets=targets, **kwargs)

    def to_tfdataset(self, *args, **kwargs):
        if "features" not in kwargs:
            kwargs["features"] = [self]

        if "total_size" not in kwargs:
            kwargs["total_size"] = len(self)

        return to_tfdataset2(*args, **kwargs)

    def to_tfdataset_(
        self, *others, align_with=None, total_size=None, merger=default_merger
    ):
        import tensorflow as tf

        if align_with is not None:
            indices = align_with._climetlab_indices
        else:
            if total_size is None:
                total_size = len(self)
            indices = tf.data.Dataset.range(total_size)

        # shuffle can happen early
        # indices = indices.shuffle(shuffle)

        def as_numpy_func(ds):
            if isinstance(ds, Base):
                func = ds._to_numpy_func()
                ds._numpy_func = func
                return func
            if hasattr(ds, "_climetlab_numpy_func"):
                return ds._climetlab_numpy_func
            raise ValueError(str(ds))

        funcs = [as_numpy_func(ds) for ds in [self, *others]]
        func = merger(*funcs)

        tfds = indices.map(to_tf_func(func))

        tfds._climetlab_n = len(others) + 1
        tfds._climetlab_tf_shape = (tfds._climetlab_n, *self[0].shape)
        tfds._climetlab_indices = indices
        tfds._climetlab_numpy_func = func
        return tfds

    def _to_tf_func(self, opt={}):
        import tensorflow as tf

        func = self._to_numpy_func(opt)

        @tf.function  # only for debugging
        def tf_map_fn(i):
            return tf.py_function(func=func, inp=[i], Tout=tf.float32)

        return tf_map_fn

    def _to_tfdataset(self, indices, opt={}):
        tfds = indices.map(self._to_tf_func(opt))
        tfds._climetlab_numpy_func = self._numpy_func
        return tfds

    def zip_with(self, *args, **kwargs):
        import tensorflow as tf

        return tf.data.Dataset.zip(tuple(self, *args), **kwargs)


def cml_tfzip(*args, **kwargs):
    import tensorflow as tf

    return tf.data.Dataset.zip(tuple(args), **kwargs)


def to_tf_func(map_fn):
    import tensorflow as tf

    @tf.function  # only for debugging
    def tf_map_fn(i):
        return tf.py_function(func=map_fn, inp=[i], Tout=tf.float32)

    return tf_map_fn
