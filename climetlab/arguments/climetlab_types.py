# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime


def _identity(x):
    return x


class Type:
    multiple = None

    def cast_to_type_list(self, value) -> list:
        if isinstance(value, (tuple, list)):
            return [self.cast_to_type(v) for v in value]
        return [self.cast_to_type(value)]

    def cast_to_type(self, value):
        return value

    def apply_format(self, value):
        print(f"{self.__class__} is formatting {value}")
        return value

    def compare(self, value, v):
        return value == v


class _EnumType(Type):
    pass


class EnumType(_EnumType):
    multiple = False


class EnumListType(_EnumType):
    multiple = True


class _StrType(Type):
    def cast_to_type(self, value):
        return str(value)

    def compare(self, value, v):
        if isinstance(value, str) and isinstance(v, str):
            return value.upper() == v.upper()
        return value == v


class StrType(_StrType):
    multiple = False


class StrListType(_StrType):
    multiple = True


class _IntType(Type):
    def cast_to_type(self, value):
        return int(value)


class IntType(_IntType):
    multiple = False


class IntListType(_IntType):
    multiple = True


class _FloatType(Type):
    def cast_to_type(self, value):
        return float(value)


class FloatType(_FloatType):
    multiple = False


class FloatListType(_FloatType):
    multiple = True


class _DateType(Type):
    def __init__(self, format=None) -> None:
        self.format = format

    def apply_format(self, value):
        if self.format is None:
            return value
        assert not isinstance(value, (list, tuple)), value
        return value.strftime(self.format)


class DateType(_DateType):
    multiple = False

    def cast_to_type(self, value):
        from climetlab.utils.dates import to_date_list

        return to_date_list(value)[0]


class DateListType(_DateType):
    multiple = True

    def cast_to_type(self, value):
        from climetlab.utils.dates import to_date_list

        return to_date_list(value)[0]  # TODO: to a todate() function


class _VariableType(Type):
    def __init__(self, convention) -> None:
        assert isinstance(convention, str), convention
        self.convention = convention

    def apply_format(self, value):
        from climetlab.utils.conventions import normalise_string

        return normalise_string(value, convention=self.convention)


class VariableType(_VariableType):
    multiple = False


class VariableListType(_VariableType):
    multiple = True


class BoundingBoxType(Type):
    multiple = False

    def __init__(self, format=None) -> None:
        self.format = format
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
        self.formatter = FORMATTERS[format]

    def cast_to_type_list(self, value) -> list:
        return [self.cast_to_type(value)]

    def cast_to_type(self, value):
        from climetlab.utils.bbox import to_bounding_box

        return to_bounding_box(value)

    def apply_format(self, value):
        return self.formatter(value)


def _find_cml_type(input_type, multiple):

    if isinstance(input_type, Type):
        if not multiple is None and hasattr(input_type, "multiple"):
            assert input_type.multiple == multiple, (input_type, multiple)
        return Type

    if not isinstance(input_type, str):
        str_type = {
            int: "int",
            float: "float",
            str: "str",
            datetime.datetime: "date",
        }[input_type]
        return _find_cml_type(str_type, multiple=multiple)

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

    if multiple is None:
        return {**LIST_TYPES, **NON_LIST_TYPES}[input_type]

    if multiple is False:
        if input_type in LIST_TYPES:
            raise ValueError(f"Cannot set multiple={multiple} and type={input_type}.")
        return NON_LIST_TYPES[input_type]

    if multiple is True:
        if input_type in LIST_TYPES:
            return LIST_TYPES[input_type]
        if input_type + "-list" in LIST_TYPES:
            return LIST_TYPES[input_type + "-list"]
        raise ValueError(
            f"Cannot set multiple={multiple} and type={input_type}. Type must be in {list(LIST_TYPES.keys())}"
        )
    return None
