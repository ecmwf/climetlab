#!/usr/bin/env python3
# (C) Copyright 2023 European Centre for Medium-Range Weather Forecasts.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import warnings
from itertools import zip_longest
from numbers import Number

import numpy as np


def default_merger(*funcs):
    if not funcs:
        return None

    def map_fn(i):
        i = int(i)
        arrays = [m(i) for m in funcs]
        array = np.stack(arrays)
        return array

    return map_fn


def as_numpy_func(ds, options=None):
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
