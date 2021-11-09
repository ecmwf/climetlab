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

    def update(self, availability):
        pass


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
            except (ValueError, TypeError):
                pass
            return False

        for v in self.values:
            if same(value, v):
                return v

        raise ValueError(
            f"Invalid value '{value}', possible values are {self.values} ({self.__class__.__name__})"
        )

    def update(self, availability):
        # TODO: if value is none : use availability w
        # else : check subset : values included into availability
        pass


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
    def _format(self, value, format):
        return value.strftime(format)

    def include_args(self, decorator, args):
        assert len(args) == 1, args
        decorator.format = args[0]


class DateType(_DateType, NonListMixin):
    def cast(self, value):
        from climetlab.utils.dates import to_date_list

        # TODO: change into to_datetime?
        lst = to_date_list(value)
        assert len(lst) == 1, lst
        return lst[0]


class DateListType(_DateType, ListMixin):
    def cast(self, value):
        from climetlab.utils.dates import to_date_list

        lst = to_date_list(value)
        return lst


class _VariableType(Type):
    def __init__(self, convention):
        self.convention = convention

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


def infer_type(**kwargs):
    LOG.debug("INFER => %s", kwargs)
    x = _infer_type(**kwargs)
    LOG.debug("INFER <= %s", x)
    return x


def _infer_type(**kwargs):
    _type = kwargs.pop("type", None)
    values = kwargs.pop("values", None)
    multiple = kwargs.pop("multiple", None)

    # TODO:
    assert not isinstance(_type, Type), f"IMPLEMENT infer_type({_type})"

    # Take care of builtin types and others
    if _type in GIVEN_TYPES:
        return infer_type(
            type=GIVEN_TYPES[_type],
            values=values,
            multiple=multiple,
            **kwargs,
        )

    # normalize("name", ["a", "b", "c"]) and similar
    if isinstance(values, (list, tuple)):  # and type is None:
        if _type not in (None, "enum", "enum-list"):
            LOG.warning(
                f"Type ignored with enums, values={values}, type={_type} and multiple={multiple}"
            )
        if multiple is None:
            multiple = _type == "enum-list"
        if multiple:
            return EnumListType(values)
        else:
            return EnumType(values)

    if values is None and isinstance(_type, str):

        if multiple is None:
            try:
                return {**LIST_TYPES, **NON_LIST_TYPES}[_type](**kwargs)
            except Exception as e:
                raise ValueError(f"Error building {_type}({kwargs}): {e}")

        if multiple is False:
            if _type in LIST_TYPES:
                raise ValueError(f"Cannot set multiple={multiple} and type={_type}.")
            return NON_LIST_TYPES[_type](**kwargs)

        if multiple is True:
            if _type in LIST_TYPES:
                return LIST_TYPES[_type]()
            if _type + "-list" in LIST_TYPES:
                return LIST_TYPES[_type + "-list"](**kwargs)
            raise ValueError(
                f"Cannot set multiple={multiple} and type={_type}. Type must be in {list(LIST_TYPES.keys())}"
            )

    raise ValueError(
        f"Cannot infer type from values={values}, type={_type} and multiple={multiple}"
    )
