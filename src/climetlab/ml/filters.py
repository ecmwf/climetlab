#!/usr/bin/env python3
# (C) Copyright 2023 European Centre for Medium-Range Weather Forecasts.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.


class YAFilter:
    def __init__(self, source):
        self.init_source = source
        self._source = None
        self._func = None

    def apply_to_source(self, source):
        # To be overridden by subclasses
        return source

    def apply_to_func(self, func):
        # To be overridden by subclasses
        return func

    @property
    def source(self):
        if self._source is None:
            self._source = self.apply_to_source(self.init_source)
        return self._source

    @property
    def func(self):
        if self._func is None:

            def fn(i):
                return self.source[i].to_numpy()

            self._func = self.apply_to_func(fn)
        return self._func

    def __call__(self, i):
        return self.func(i)


class NormaliseFilter(YAFilter):
    def __init__(self, source, a, b):
        super().__init__(source)
        self.a = a
        self.b = b

    def apply_to_func(self, func):
        def fn(i):
            arr = func(i)
            arr = self.a * arr + self.b
            return arr

        return fn


class NormaliseMeanStdFilter(YAFilter):
    def __init__(self, source):
        a, b = compute_mean_std_from_source(source)  # noqa: TODO
        super().__init__(source, a, b)


class NormaliseMinMaxFilter(YAFilter):
    def __init__(self, source):
        a, b = compute_min_max_from_source(source)  # noqa: TODO
        super().__init__(source, a, b)


class OffsetFilter(YAFilter):
    def __init__(self, offset):
        self.offset = offset

    def apply_to_source(self, source):
        # Create a Wrapper class?
        # decrease the len
        return source

    def apply_to_func(self, func):
        def fn(i):
            return func(i + self.offset)

        return fn
