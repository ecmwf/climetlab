# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# TODO: Use magics types

from . import magics_keys_parameters
from .colour import Colour


class NoConvertion:
    def convert(self, name, value):
        return value


class Bool:
    def convert(self, name, value):
        return bool(value)


class Float:
    def convert(self, name, value):
        return float(value)


class Int:
    def convert(self, name, value):
        return int(value)


class String:
    def convert(self, name, value):
        return str(value)


class ColourList:
    def convert(self, name, value):
        assert isinstance(value, (list, tuple))
        colour = Colour()
        return [colour.convert(name, x) for x in value]


class FloatList:
    def convert(self, name, value):
        assert isinstance(value, (list, tuple))
        return [float(x) for x in value]


class IntList:
    def convert(self, name, value):
        assert isinstance(value, (list, tuple))
        return [int(x) for x in value]


class StringList:
    def convert(self, name, value):
        assert isinstance(value, (list, tuple))
        return [str(x) for x in value]


def convert(action, args):

    magics_keys = magics_keys_parameters(action)

    converted = {}
    for k, v in args.items():
        klass = magics_keys.get(k, {}).get("type", "NoConvertion")
        klass = globals().get(klass, NoConvertion)()

        converted[k] = klass.convert(k, v)

    return converted
