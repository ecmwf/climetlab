# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import functools
import inspect

from climetlab.utils.bbox import BoundingBox, to_bounding_box
from climetlab.utils.conventions import normalise_string
from climetlab.utils.dates import to_date_list


class ParameterNormaliser:
    def __init__(self, convention=None):
        self.convention = convention

    def __call__(self, parameter):
        if isinstance(parameter, (list, tuple)):
            return [normalise_string(p, convention=self.convention) for p in parameter]
        else:
            return normalise_string(parameter, convention=self.convention)


CONVERT = {
    list: lambda x: x.as_list(),
    tuple: lambda x: x.as_tuple(),
    dict: lambda x: x.as_dict(),
    BoundingBox: lambda x: x,
}


class BoundingBoxNormaliser:
    def __init__(self, format=BoundingBox):
        self.format = format

    def __call__(self, bbox):
        bbox = to_bounding_box(bbox)
        return CONVERT[self.format](bbox)


class DateListNormaliser:
    def __init__(self, list=False, format=None):
        self.format = format

    def __call__(self, dates):
        dates = to_date_list(dates)
        if self.format is not None:
            dates = [d.strftime(self.format) for d in dates]
        return dates


class EnumNormaliser:
    def __init__(self, values=tuple()):
        self.values = values

    def __call__(self, value):
        for n in self.values:
            if value.lower() == n.lower():
                return n
        raise ValueError(value)


NORMALISERS = {
    "date-list": DateListNormaliser,
    "parameter-list": ParameterNormaliser,
    "bounding-box": BoundingBoxNormaliser,
}


def _normalizer(v):

    if callable(v):
        return v

    if isinstance(v, list):
        return EnumNormaliser(*v)

    if isinstance(v, str):
        v = v.split(":")

    # if hasattr(v, "normalise"):
    #     return v
    # elif hasattr(v[0], "normalise"):
    #     assert len(v) == 1, v
    #     return v[0]
    # else:
    return NORMALISERS[v[0]](*v[1:])


def _identity(x):
    return x


def normalize_args(**kwargs):
    normalizers = {}

    for k, v in kwargs.items():
        normalizers[k] = _normalizer(v)

    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            normalized = {}
            for arg, value in inspect.getcallargs(func, *args, **kwargs).items():
                normalizer = normalizers.get(arg, _identity)
                normalized[arg] = normalizer(value)
            return func(**normalized)

        return inner

    return outer
