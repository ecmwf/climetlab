# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

from climetlab.arguments.climetlab_types import Type

LOG = logging.getLogger(__name__)


class _all:
    def __repr__(self):
        return "climetlab.ALL"


ALL = _all()


class Action:
    def execute(self, kwargs):
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.__class__}"


class ArgumentTransformer(Action):
    def execute(self, kwargs):
        kwargs[self.name] = self.transform(kwargs[self.name])
        return kwargs

    def transform(self, value):
        raise NotImplementedError(self.__class__.__name__)


class AliasTransformer(ArgumentTransformer):
    def __init__(self, name, cmltype, alias, _all=None) -> None:
        self.name = name
        assert isinstance(alias, dict) or callable(alias) or alias is None
        self.alias = alias
        self._all = _all
        self.cmltype = cmltype
        self.cmltype.check_aliases(self.alias, name=self.name)

    def _apply_to_value_once(self, value):
        if value == ALL:
            assert self._all, "Cannot find values for 'ALL'"
            return self._all

        if isinstance(value, (tuple, list)):
            return [self.transform(v) for v in value]

        if callable(self.alias):
            return self.alias(value)

        if isinstance(self.alias, dict):
            try:
                return self.alias[value]
            except KeyError:  # No alias for this value
                pass
            except TypeError:  # if value is not hashable
                pass
            return value

        assert False, (self.name, self.alias)

    def transform(self, value):
        old = object()
        while old != value:
            old = value
            value = self._apply_to_value_once(old)
        return value

    def __repr__(self) -> str:
        return f"Alias({self.name}, {self.alias})"


class FormatTransformer(ArgumentTransformer):
    def __init__(self, name, type, format) -> None:
        self.name = name
        self.type = type if isinstance(type, Type) else type()
        self.format = format

    def transform(self, value):
        return self.type.format(value, self.format)

    def __repr__(self) -> str:
        txt = "Format("
        txt += f"{self.name}"
        txt += f",{self.type},format={self.format})"
        return txt


class TypeTransformer(ArgumentTransformer):
    def __init__(self, name, type) -> None:
        self.name = name
        self.type = type

    def transform(self, value):
        return self.type.cast(value)

    def __repr__(self) -> str:
        txt = "TypeTransformer("
        txt += f"{self.name}"
        txt += f",{self.type}"
        txt += ")"
        return txt


class EnumChecker(ArgumentTransformer):
    def __init__(self, name, values, type) -> None:
        self.name = name
        self.values = values
        self.type = type

    def transform(self, value):
        if not self.type.contains(value, self.values):
            raise ValueError(f"Value {value} is not in {self.values}")
        return value

    def __repr__(self) -> str:
        return f"EnumChecker({self.name}, {self.values}, type={self.type})"


class CanonicalizeTransformer(ArgumentTransformer):
    def __init__(self, name, values, type) -> None:
        self.name = name
        self.values = values
        self.type = type

    def transform(self, value):
        print(f"       canonicalizing {value}")
        return self.type.canonicalize(value, self.values)

    def __repr__(self) -> str:
        return f"Canonicalizer({self.name}, {self.values}, type={self.type})"


class AvailabilityChecker(Action):
    def __init__(self, availability) -> None:
        self.availability = availability

    def execute(self, kwargs):
        if not isinstance(kwargs, dict):
            return kwargs
        LOG.debug("Checking availability for %s", kwargs)
        # kwargs2 = deepcopy(kwargs)

        def stringify(s):
            if isinstance(s, (list, tuple)):
                return [stringify(x) for x in s]

            if isinstance(s, dict):
                r = {}
                for k, v in s.items():
                    r[k] = stringify(v)
                return r

            return str(s)

        print("---------")
        self.availability.check(stringify(kwargs))
        return kwargs

    def __repr__(self) -> str:
        txt = "Availability:"
        for line in self.availability.tree().split("\n"):
            if line:
                txt += "\n    " + line
        return txt
