# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from climetlab.utils.conventions import normalise_string
from climetlab.utils.bbox import BoundingBox
LOG = logging.getLogger(__name__)


def _identity(x):
    return x


class Normaliser:
    pass


class VariableNormaliser(Normaliser):
    def visit(self, decorator, convention=None) -> None:
        def format(parameter):
            if isinstance(parameter, (list, tuple)):
                return [normalise_string(p, convention=convention) for p in parameter]
            else:
                return normalise_string(parameter, convention=convention)

        decorator.format = format


class BoundingBoxNormaliser(Normaliser):
    def __init__(self, decorator, format=None) -> None:
        self.format = format

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
        format_one = FORMATS[format]

        def formatter(bbox):
            return [format_one(bbox) for b in bbox]

        decorator.formatter = format


class DateNormaliser(Normaliser):
    def visit(self, decorator, format=None) -> None:
        def format(dates):
            return [d.strftime(format) for d in dates]

        decorator.format = format


class EnumNormaliser(Normaliser):
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

    def visit(self, decorator, format=None) -> None:
        ENUM_FORMATTER = {
            int: int,
            str: str,
            float: float,
            None: _identity,
            "int": int,
            "str": str,
            "float": float,
        }

        def norm(x):
            if x is ALL:
                return self.values
            if x is None:  # TODO: To be discussed
                return self.values

            return [self.normalize_one_value(y) for y in x]

        decorator.format = ENUM_FORMATTER[format]
        decorator.norm = norm

    def normalize_one_value(self, x):
        if not self.values:
            return x

        for v in self.values:
            if self.compare(x, v):
                return v
        self.raise_error(x)
