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
            if isinstance(a, str) and isinstance(b, str):
                return a.upper() == b.upper()
            return a == b

        for v in self.values:
            if same(value, v):
                return v

        raise ValueError(
            f"Invalid value '{value}', possible values are {self.values} ({self.type})"
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

    def _format(self, value, format):
        return format % value


class StrType(_StrType, NonListMixin):
    pass


class StrListType(_StrType, ListMixin):
    pass


class _IntType(Type):
    def _cast(self, value):
        return int(value)

    def _format(self, value, format):
        return format % value


class IntType(_IntType, NonListMixin):
    pass


class IntListType(_IntType, ListMixin):
    pass


class _FloatType(Type):
    def _cast(self, value):
        return float(value)

    def _format(self, value, format):
        return format % value


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

    def _format(self, value, format):
        return format % value


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


def _find_cml_type(input_type, multiple):

    if isinstance(input_type, Type):
        if multiple is not None and hasattr(input_type, "multiple"):
            assert input_type.multiple == multiple, (input_type, multiple)
        return input_type

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
        return {**LIST_TYPES, **NON_LIST_TYPES}[input_type]()

    if multiple is False:
        if input_type in LIST_TYPES:
            raise ValueError(f"Cannot set multiple={multiple} and type={input_type}.")
        return NON_LIST_TYPES[input_type]()

    if multiple is True:
        if input_type in LIST_TYPES:
            return LIST_TYPES[input_type]()
        if input_type + "-list" in LIST_TYPES:
            return LIST_TYPES[input_type + "-list"]()
        raise ValueError(
            f"Cannot set multiple={multiple} and type={input_type}. Type must be in {list(LIST_TYPES.keys())}"
        )
    print(f"Cannot find cml_type for {input_type}")
    return None


def infer_type(values, type, multiple):

    if type is None and multiple is None:
        if (isinstance(values, tuple) and multiple is None) or (isinstance(values, list, tuple) and not multiple):
            return EnumType(values)

        if (isinstance(values, list) and multiple is None) or (isinstance(values, list, tuple) and multiple):
            return EnumListType(values)

    if type is not None:
        return type
