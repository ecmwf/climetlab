# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import logging
import re

LOG = logging.getLogger(__name__)


def _identity(x):
    return x


class ListMixin:
    def cast(self, value):
        if isinstance(value, tuple):  # We choose list over tuple
            value = list(value)
        if not isinstance(value, list):
            value = [value]

        return [self._cast(v) for v in value]

    def format(self, value, format):
        return [self._format(v, format) for v in value]


class NonListMixin:
    def cast(self, value):
        return self._cast(value)

    def format(self, value, format):
        return self._format(value, format)


class Type:
    def _cast(self, value):
        raise NotImplementedError(self.__class__)

    def _format(self, value, format):
        return format % (value,)

    def __repr__(self):
        return self.__class__.__name__


class _EnumType(Type):
    def __init__(self, values):
        self.values = values

    def _cast(self, value):
        def same(a, b):
            if a == b:
                return True
            try:
                return a.upper() == b.upper()
            except AttributeError:
                pass
            try:
                return float(a) == float(b)
            except TypeError:
                pass
            return False

        for v in self.values:
            if same(value, v):
                return v

        raise ValueError(
            f"Invalid value '{value}', possible values are {self.values} ({self.__class__.__name__})"
        )


class EnumType(_EnumType, NonListMixin):
    pass


class EnumListType(_EnumType, ListMixin):
    def cast(self, value):
        from climetlab.arguments.transformers import ALL

        if value is ALL:
            return self.values
        return super().cast(value)


class _StrType(Type):
    def _cast(self, value):
        return str(value)


class StrType(_StrType, NonListMixin):
    pass


class StrListType(_StrType, ListMixin):
    pass


class _IntType(Type):
    def _cast(self, value):
        return int(value)


class IntType(_IntType, NonListMixin):
    pass


class IntListType(_IntType, ListMixin):
    pass


class _FloatType(Type):
    def _cast(self, value):
        return float(value)


class FloatType(_FloatType, NonListMixin):
    pass


class FloatListType(_FloatType, ListMixin):
    pass


class _DateType(Type):
    def _cast(self, value):
        from climetlab.utils.dates import to_date_list

        lst = to_date_list(value)
        assert len(lst) == 1, lst
        return lst[0]

    def _format(self, value, format):
        return value.strftime(format)

    def include_args(self, decorator, args):
        assert len(args) == 1, args
        decorator.format = args[0]


class DateType(_DateType, NonListMixin):
    pass


class DateListType(_DateType, ListMixin):
    pass


class _VariableType(Type):
    def __init__(self, convention):
        self.convention = convention

    def include_args(self, decorator, args):
        assert len(args) == 1, args
        decorator.format = args[0]

    def _cast(self, value):
        from climetlab.utils.conventions import normalise_string

        return normalise_string(str(value), convention=self.convention)


class VariableType(_VariableType, NonListMixin):
    pass


class VariableListType(_VariableType, ListMixin):
    pass


class BoundingBoxType(Type, NonListMixin):
    def include_args(self, decorator, args):
        assert len(args) == 1, args
        decorator.format = args[0]

    def cast(self, value):
        from climetlab.utils.bbox import to_bounding_box

        return to_bounding_box(value)

    def format(self, value, format):
        from climetlab.utils.bbox import BoundingBox

        FORMATTERS = {
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
        formatter = FORMATTERS[format]
        return formatter(value)


GIVEN_TYPES = {
    int: "int",
    float: "float",
    str: "str",
    datetime.datetime: "date",
    bool: "bool",  # TODO: implement me
}

NON_LIST_TYPES = {
    "int": IntType,
    "float": FloatType,
    "str": StrType,
    "enum": EnumType,
    "date": DateType,
    "variable": VariableType,
    "bounding-box": BoundingBoxType,
    "bbox": BoundingBoxType,
}
LIST_TYPES = {
    "int-list": IntListType,
    "float-list": FloatListType,
    "str-list": StrListType,
    "enum-list": EnumListType,
    "date-list": DateListType,
    "variable-list": VariableListType,
}

OPTIONS = {
    "date": ("format",),
    "date-list": ("format",),
    "bounding-box": ("format",),
    "bbox": ("format",),
}


def infer_type(values, type, multiple, options, *args, **kwargs):

    # TODO:
    assert not isinstance(type, Type), f"IMPLEMENT infer_type({type})"

    # Take care of builtin types and others
    if type in GIVEN_TYPES:
        return infer_type(values, GIVEN_TYPES[type], multiple, options, *args, **kwargs)

    # normalize("name", ["a", "b", "c"]) and similar
    if isinstance(values, (list, tuple)):  # and type is None:
        if type is not None:
            LOG.warning(
                f"Type ignored with enums, values={values}, type={type} and multiple={multiple}"
            )
        if multiple is False or (isinstance(values, tuple) and multiple is None):
            return EnumType(values)

        if multiple is True or (isinstance(values, list) and multiple is None):
            return EnumListType(values)

    if isinstance(values, str) and type is None:
        if "(" in values:
            m = re.match(r"(.+)\((.+)\)", values)
            type = m.group(1)
            args = m.group(2).split(",")
        else:
            type = values
            args = []

        if args:
            # Remove
            for a, o in zip(args, OPTIONS.get(type, [])):
                options[o] = a
            args = args[len(OPTIONS.get(type, [])) :]

        return infer_type(None, type, multiple, options, *args, **kwargs)

    if values is None and isinstance(type, str):
        print("----->", type, args)
        if multiple is None:
            try:
                return {**LIST_TYPES, **NON_LIST_TYPES}[type](*args, **kwargs)
            except Exception as e:
                raise ValueError(f"Error building {type}({args}{kwargs}): {e}")

        if multiple is False:
            if type in LIST_TYPES:
                raise ValueError(f"Cannot set multiple={multiple} and type={type}.")
            return NON_LIST_TYPES[type](*args, **kwargs)

        if multiple is True:
            if type in LIST_TYPES:
                return LIST_TYPES[type]()
            if type + "-list" in LIST_TYPES:
                return LIST_TYPES[type + "-list"](*args, **kwargs)
            raise ValueError(
                f"Cannot set multiple={multiple} and type={type}. Type must be in {list(LIST_TYPES.keys())}"
            )

    # Place older for availability, assuming Enum
    if values is None and type is None and multiple is not None:
        if multiple:
            return EnumListType(values)
        else:
            return EnumType(values)

    raise ValueError(
        f"Cannot infer type from values={values}, type={type} and multiple={multiple}"
    )
