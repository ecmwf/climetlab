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


ENUM_FORMATTER = {
    int: int,
    str: str,
    float: float,
    None: _identity,
    "int": int,
    "str": str,
    "float": float,
}


class _EnumNormaliser:
    def __init__(self, values, format=None):
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

        if values is None:
            values = []

        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            values = values[0]

        self.values = values
        self.format = ENUM_FORMATTER[format]

    def __repr__(self):
        txt = f"{type(self)}("
        txt += ",".join([str(k) for k in self.values])
        txt += f", format={self.format}"
        txt += ")"
        return txt

    def normalize_one_value(self, x):
        if not self.values:
            return x

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
    def __call__(self, x):
        return self.format(self.normalize_one_value(x))

    def normalize(self, x):
        return self.normalize_one_value(x)


class EnumListNormaliser(_EnumNormaliser):
    def __call__(self, x):
        return self.format_all(self.normalize_multiple_values(x))

    def normalize(self, x):
        return self.normalize_multiple_values(x)

    def normalize_multiple_values(self, x):
        if x is ALL:
            return self.format_all(self.values)
        if x is None:  # TODO: To be discussed
            return self.format_all(self.values)

        if not isinstance(x, (list, tuple)):
            x = [x]

        return [self.normalize_one_value(y) for y in x]

    def format_all(self, values):
        return [self.format(x) for x in values]


NORMALISERS = {
    "enum": EnumNormaliser,
    "enum-list": EnumListNormaliser,
    "date-list": DateListNormaliser,
    "date": DateNormaliser,
    "variable-list": VariableNormaliser,
    "bounding-box": BoundingBoxNormaliser,
    "bbox": BoundingBoxNormaliser,
    (str, False): EnumNormaliser,
    (str, True): EnumListNormaliser,
    (int, False): EnumNormaliser,
    (int, True): EnumListNormaliser,
}


def _kwargs_to_normalizer(**kwargs):

    type = kwargs.pop("type", str)
    multiple = kwargs.pop("multiple", True)

    # TODO: check
    kwargs.setdefault("format", type)

    return NORMALISERS[(type, multiple)](**kwargs)


def _find_normaliser(values, **kwargs):

    if kwargs:
        return _kwargs_to_normalizer(values=values, **kwargs)

    if callable(values):
        return values

    if isinstance(values, tuple):
        return EnumNormaliser(values)

    if isinstance(values, list):
        return EnumListNormaliser(values)

    assert isinstance(values, str), values
    m = re.match(r"(.+)\((.+)\)", values)

    if not m:
        return NORMALISERS[values]()

    args = m.group(2).split(",")
    name = m.group(1)
    return NORMALISERS[name](*args)
