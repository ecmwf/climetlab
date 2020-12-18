# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import re
from .datetime import to_datetime

RE1 = re.compile(r"{([^}]*)}")
RE2 = re.compile(r"\(([^}]*)\)")


class Any:
    def substitute(self, value):
        return value


class Int:
    def __init__(self, format="%d"):
        self.format = format

    def substitute(self, value):
        assert isinstance(value, int)
        return self.format % value


class Float:
    def __init__(self, format="%g"):
        self.format = format

    def substitute(self, value):
        assert isinstance(value, (int, float))
        return self.format % value


class Datetime:
    def __init__(self, format):
        self.format = format

    def substitute(self, value):
        return to_datetime(value).strftime(self.format)


class Str:
    def __init__(self, format="%s"):
        self.format = format

    def substitute(self, value):
        assert isinstance(value, str)
        return self.format % value


TYPES = {"": Any, "int": Int, "float": Float, "date": Datetime}


class Constant:

    name = None

    def __init__(self, value):
        self.value = value

    def substitute(self, params):
        return self.value


class Variable:
    def __init__(self, value):
        bits = value.split(":")
        self.name = bits[0]
        kind = RE2.split(":".join(bits[1:]))
        if len(kind) == 1:
            self.kind = TYPES[kind[0]]()
        else:
            self.kind = TYPES[kind[0]](kind[1])

    def substitute(self, params):
        return self.kind.substitute(params[self.name])


class Pattern:
    def __init__(self, pattern):

        self.pattern = []
        self.variables = []
        for i, p in enumerate(RE1.split(pattern)):
            if i % 2 == 0:
                self.pattern.append(Constant(p))
            else:
                v = Variable(p)
                self.variables.append(v)
                self.pattern.append(v)

    @property
    def names(self):
        return sorted(set(v.name for v in self.variables))

    def substitute(self, *args, **kwargs):
        params = {}
        for a in args:
            params.update(a)
        params.update(kwargs)

        used = set(params.keys())
        result = []
        for p in self.pattern:
            used.discard(p.name)
            result.append(p.substitute(params))
        if used:
            raise ValueError("Unused parameters: {}".format(used))

        return "".join([str(x) for x in result])
