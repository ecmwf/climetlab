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
import re

from climetlab.utils.bbox import BoundingBox, to_bounding_box
from climetlab.utils.conventions import normalise_string
from climetlab.utils.dates import to_date_list


class _all:
    def __repr__(self):
        return "climetlab.normalize.ALL"


ALL = _all()


def _identity(x):
    return x


class VariableNormaliser:
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
    BoundingBox: _identity,
    "list": lambda x: x.as_list(),
    "tuple": lambda x: x.as_tuple(),
    "dict": lambda x: x.as_dict(),
    "BoundingBox": _identity,
}


class BoundingBoxNormaliser:
    def __init__(self, format=BoundingBox):
        self.format = format

    def __call__(self, bbox):
        bbox = to_bounding_box(bbox)
        return CONVERT[self.format](bbox)


class DateListNormaliser:
    def __init__(self, format=None):
        self.format = format

    def __call__(self, dates):
        dates = to_date_list(dates)
        if self.format is not None:
            dates = [d.strftime(self.format) for d in dates]
        return dates


class DateNormaliser:
    def __init__(self, format=None):
        self.format = format

    def __call__(self, dates):
        dates = to_date_list(dates)
        if self.format is not None:
            dates = [d.strftime(self.format) for d in dates]
        assert len(dates) == 1
        return dates[0]


class _EnumNormaliser:
    def __init__(self, *values):
        """Initialize the parameter instance .

        Parameters
        ----------
        values : [type]
            [description]

        Raises
        ------
        ValueError
            Ret[description]
        """

        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            values = values[0]

        self.values = values

    def normalize_one_value(self, x):
        for v in self.values:
            if self.compare(x, v):
                return v
        self.raise_error(x)

    def compare(self, x, value):
        if isinstance(x, str) and isinstance(value, str):
            return x.upper() == value.upper()
        return x == value

    def raise_error(self, x):
        raise ValueError(f'Invalid value "{x}", possible values are {self.values}')


class EnumNormaliser(_EnumNormaliser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, x):
        return self.normalize_one_value(x)


class EnumListNormaliser(_EnumNormaliser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, x):
        if x is ALL:
            return self.values
        if x is None:  # TODO: To be discussed
            return self.values

        if not isinstance(x, (list, tuple)):
            x = [x]

        return [self.normalize_one_value(y) for y in x]


NORMALISERS = {
    "enum": EnumNormaliser,
    "enum-list": EnumListNormaliser,
    "date-list": DateListNormaliser,
    "date": DateNormaliser,
    "variable-list": VariableNormaliser,
    "bounding-box": BoundingBoxNormaliser,
    "bbox": BoundingBoxNormaliser,
}


def _find_normaliser(v):

    if callable(v):
        return v

    if isinstance(v, tuple):
        return EnumNormaliser(v)

    if isinstance(v, list):
        return EnumListNormaliser(v)

    assert isinstance(v, str), v
    m = re.match(r"(.+)\((.+)\)", v)

    if not m:
        return NORMALISERS[v]()

    args = m.group(2).split(",")
    name = m.group(1)
    return NORMALISERS[name](*args)


def normalize_args(**kwargs):
    normalizers = {}

    for k, v in kwargs.items():
        normalizers[k] = _find_normaliser(v)

    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            provided = inspect.getcallargs(func, *args, **kwargs)
            for name, param in inspect.signature(func).parameters.items():
                # See https://docs.python.org/3.5/library/inspect.html#inspect.signature
                assert param.kind is not param.VAR_POSITIONAL
                if param.kind is param.VAR_KEYWORD:
                    provided.update(provided.pop(name, {}))

            normalized = {}
            for arg, value in provided.items():
                normalizer = normalizers.get(arg, _identity)
                normalized[arg] = normalizer(value)
            return func(**normalized)

        return inner

    return outer
