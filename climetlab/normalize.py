# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import re

from climetlab.utils.bbox import BoundingBox, to_bounding_box
from climetlab.utils.conventions import normalise_string
from climetlab.utils.dates import to_date_list

LOG = logging.getLogger(__name__)


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
        return parameter


class VariableFormatter:
    def __init__(self, convention=None):
        self.convention = convention

    def __call__(self, parameter):
        if isinstance(parameter, (list, tuple)):
            return [normalise_string(p, convention=self.convention) for p in parameter]
        else:
            return normalise_string(parameter, convention=self.convention)


class BoundingBoxNormaliser:
    def __call__(self, bbox):
        return to_bounding_box(bbox)


class BoundingBoxFormatter:
    def __init__(self, format=None) -> None:
        FORMATS = {
            list: lambda x: x.as_list(),
            tuple: lambda x: x.as_tuple(),
            dict: lambda x: x.as_dict(),
            BoundingBox: _identity,
            "list": lambda x: x.as_list(),
            "tuple": lambda x: x.as_tuple(),
            "dict": lambda x: x.as_dict(),
            "BoundingBox": _identity,
            None: _identity,
        }
        self.format = FORMATS[format]

    def __call__(self, bbox):
        return [self.format(bbox) for b in bbox]


class DateNormaliser:
    def __call__(self, dates):
        return to_date_list(dates)


class DateFormatter:
    def __call__(self, dates):
        return [d.strftime(self.cast_type) for d in dates]


ENUM_FORMATTER = {
    int: int,
    str: str,
    float: float,
    None: _identity,
    "int": int,
    "str": str,
    "float": float,
}


class EnumNormaliser:
    def __init__(self, values):
        if values is None:
            values = []

        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            values = values[0]

        self.values = values

    def __repr__(self):
        txt = f"{type(self)}("
        txt += ",".join([str(k) for k in self.values])
        txt += ")"
        return txt

    def compare(self, x, value):
        if isinstance(x, str) and isinstance(value, str):
            return x.upper() == value.upper()
        return x == value

    def raise_error(self, x):
        raise ValueError(
            f'Invalid value "{x}"({type(x)}), possible values are {self.values}'
        )

    def __call__(self, x):
        if x is ALL:
            return self.values
        if x is None:  # TODO: To be discussed
            return self.values

        return [self.normalize_one_value(y) for y in x]

    def normalize_one_value(self, x):
        if not self.values:
            return x

        for v in self.values:
            if self.compare(x, v):
                return v
        self.raise_error(x)


def _find_normaliser(values):

    if callable(values):
        return values

    if isinstance(values, (tuple, list)):
        return EnumNormaliser(values)

    assert isinstance(values, str), values
    m = re.match(r"(.+)\((.+)\)", values)

    if not m:
        return NORMALISERS[values]()

    args = m.group(2).split(",")
    name = m.group(1)
    return NORMALISERS[name](*args)
