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
        if not isinstance(value, (tuple, list)):
            return self.cast([value])
        return [self._cast(v) for v in value]

    def canonicalize(self, value, values):
        return [self._canonicalize(v, values) for v in value]

    def contains(self, value, values):
        return all([self._contains(v, values) for v in value])

    def format(self, value, format):
        return [self._format(v, format) for v in value]


class NonListMixin:
    def cast(self, value):
        return self._cast(value)

    def canonicalize(self, value, values):
        return self._canonicalize(self, value, values)

    def contains(self, value, values):
        return self._contains(value, values)

    def format(self, value, format):
        return self._format(value, format)


class Type:
    multiple = None

    def include_args(self, decorator, args):
        args = [f" '{v}'" for v in args]
        raise NotImplementedError(
            f"Cannot process additional arguments:{','.join([v for v in args])}."
        )

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

    def _contains(self, value, values):
        return value in values

    def check_aliases(self, aliases, name=None):
        if self.multiple is False:
            for k, v in aliases.items():
                if isinstance(v, (tuple, list)):
                    raise ValueError(
                        f"Cannot alias to a list for '{name}' of type {self.__class__} with alias {k}={v}."
                    )


class _EnumType(Type):
    pass


class EnumType(_EnumType):
    pass


class EnumListType(_EnumType):
    pass


class _StrType(Type):
    def _cast(self, value):
        return str(value)

    def compare(self, value, v):
        if isinstance(value, str) and isinstance(v, str):
            return value.upper() == v.upper()
        return value == v

    def _canonicalize(self, value, values):
        for v in values:
            if self.compare(v, value):
                return v
        raise ValueError(
            f'Invalid value "{value}"({type(value)}), possible values are {values}'
        )


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
    def format(self, value, format):
        return format % value


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
    def include_args(self, decorator, args):
        assert len(args) == 1, args
        decorator.format = args[0]

    def _cast(self, value):
        return str(value)

    def _format(self, value, convention):
        from climetlab.utils.conventions import normalise_string

        return normalise_string(value, convention=convention)


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
