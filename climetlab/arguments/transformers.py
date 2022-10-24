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
from climetlab.vocabularies.aliases import unalias

LOG = logging.getLogger(__name__)


class _all:
    def __repr__(self):
        return "climetlab.ALL"


ALL = _all()


class Action:
    def execute(self, kwargs):
        raise NotImplementedError()

    def execute_before_default(self, kwargs):
        return kwargs

    def __repr__(self) -> str:
        return f"{self.__class__}"


class ArgumentTransformer(Action):
    def __init__(self, owner):
        self.owner = owner

    def execute(self, kwargs):
        if self.name in kwargs:  # TODO: discuss that
            kwargs[self.name] = self.transform(kwargs[self.name])
        return kwargs

    def transform(self, value):
        raise NotImplementedError(self.__class__.__name__)

    @property
    def name(self):
        if self.owner is None:
            return "-"
        if isinstance(self.owner, str):
            return self.owner
        return self.owner.name


class _TypedTransformer(ArgumentTransformer):
    def __init__(self, owner, type) -> None:
        super().__init__(owner)
        self.type = type if isinstance(type, Type) else type()


class AliasTransformer(_TypedTransformer):
    def __init__(self, owner, type, aliases) -> None:
        super().__init__(owner, type)
        self.aliases = aliases

        if isinstance(self.aliases, str):
            self.unalias = self.from_string
            return

        if isinstance(self.aliases, dict):
            self.unalias = self.from_dict
            return

        if callable(self.aliases):
            self.unalias = self.aliases
            return

        self.unalias = self.unsupported

    def unsupported(self, value):
        raise NotImplementedError(self.aliases)

    def from_string(self, value):
        return unalias(self.aliases, value)

    def from_dict(self, value):
        try:
            return self.aliases[value]
        except KeyError:  # No alias for this value
            pass
        except TypeError:  # if value is not hashable
            pass

        return value

    def _transform_one(self, value):
        old = object()
        while old != value:
            old = value
            value = self.unalias(old)
            LOG.debug("    Unalias %s --> %s", old, value)
        return value

    def transform(self, value):
        LOG.debug("    Unaliasing %s", value)
        if isinstance(value, list):
            return [self._transform_one(v) for v in value]
        if isinstance(value, tuple):
            return tuple([self._transform_one(v) for v in value])
        return self._transform_one(value)

    def __repr__(self) -> str:
        return f"AliasTransformer({self.owner},{self.aliases},{self.type})"


class FormatTransformer(_TypedTransformer):
    def __init__(self, owner, format, type) -> None:
        super().__init__(owner, type)
        self.format = format

    def transform(self, value):
        if value is None:
            return value
        return self.type.format(value, self.format)

    def __repr__(self) -> str:
        return f"FormatTransformer({self.owner},{self.format},{self.type})"


class TypeTransformer(_TypedTransformer):
    def __init__(self, owner, type):
        super().__init__(owner, type)

    def transform(self, value):
        if value is None:
            return value
        return self.type.cast(value)

    def __repr__(self) -> str:
        return f"TypeTransformer({self.owner},{self.type}"


class AvailabilityChecker(Action):
    def __init__(self, availability) -> None:
        self.availability = availability

    def execute(self, kwargs):
        LOG.debug("Checking availability for %s", kwargs)
        assert isinstance(kwargs, dict), kwargs
        without_none = {k: v for k, v in kwargs.items() if v is not None}
        self.availability.check(without_none)
        return kwargs

    def __repr__(self) -> str:
        txt = "Availability:"
        for line in self.availability.tree().split("\n"):
            if line:
                txt += "\n    " + line
        return txt


class KwargsAliasTransformer(Action):
    def __init__(self, alias_argument) -> None:
        self.aliases = alias_argument.kwargs

    def execute(self, kwargs):
        return kwargs

    def execute_before_default(self, kwargs):
        if kwargs:
            LOG.debug("Transforming kwargs names with aliases for %s", kwargs)
        assert isinstance(kwargs, dict), kwargs
        new_kwargs = {}
        for k, v in kwargs.items():
            new_k = self.reversed_aliases.get(k, k)
            assert (
                new_k not in new_kwargs
            ), f"Error: Multiple values were given for aliased arguments: with '{k}' and '{new_k}'."
            new_kwargs[new_k] = v
        return new_kwargs

    @property
    def reversed_aliases(self):
        reversed = {}
        for target, aliases in self.aliases.items():
            for alias in aliases:
                assert alias not in reversed, (
                    "Error: Multiple target value for alias "
                    f" argument '{alias}': '{target}' and '{reversed[alias]}'"
                )
                reversed[alias] = target
        return reversed

    def __repr__(self) -> str:
        txt = "KwargsAlias:"
        txt += ",".join([f"{v}->{k}" for k, v in self.aliases.items()])
        return txt
