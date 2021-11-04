# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


def _identity(x):
    return x


class Type:
    def cast_to_type(self, value):
        return value

    def apply_format(self, value):
        print(f"{self.__class__} is formatting {value}")
        return value


class StrType(Type):
    def cast_to_type(self, value):
        return str(value)


class IntType(Type):
    def cast_to_type(self, value):
        return int(value)


class FloatType(Type):
    def cast_to_type(self, value):
        return float(value)


class DateType(Type):
    def __init__(self, format=None) -> None:
        self.format = format

    def cast_to_type(self, value):
        from climetlab.utils.dates import to_date_list

        return to_date_list(value)[0]  # TODO: to a todate() function

    def apply_format(self, value):
        if self.format is None:
            return value
        assert not isinstance(value, (list, tuple)), value
        return value.strftime(self.format)


class VariableType(Type):
    def __init__(self, convention) -> None:
        assert isinstance(convention, str), convention
        self.convention = convention

    def apply_format(self, value):
        from climetlab.utils.conventions import normalise_string

        return normalise_string(value, convention=self.convention)


class BoundingBoxType(Type):
    def __init__(self, format) -> None:
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

    def cast_to_type(self, value):
        from climetlab.utils.bbox import to_bounding_box

        return to_bounding_box(value)

    def apply_format(self, value):
        return self.formatter(value)
