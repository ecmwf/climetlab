# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import inspect
import logging
import os

from climetlab.utils.availability import Availability

LOG = logging.getLogger(__name__)


class Transformer:
    enabled = True

    def valid_with_multiple(self, multiple_transformer):
        pass

    def __call__(self, kwargs):
        if not self.enabled:
            return kwargs
        return self._apply_to_kwargs(kwargs)


class ArgumentTransformer(Transformer):
    def __init__(self, name) -> None:
        self.name = name

    def _apply_to_kwargs(self, kwargs):
        if self.name not in kwargs:
            return kwargs
        kwargs[self.name] = self.apply_to_value(kwargs[self.name])
        return kwargs

    def apply_to_value(self, value):
        raise NotImplementedError()


class MultipleTransformer(ArgumentTransformer):
    def __init__(self, name, multiple) -> None:
        super().__init__(name)
        assert multiple in [True, False, None]
        self.multiple = multiple

    @property
    def enabled(self):
        return not self.multiple is None

    def apply_to_value(self, value):
        is_list = isinstance(value, (list, tuple))
        if self.multiple and not is_list:
            return [value]
        if not self.multiple and is_list:
            assert len(value) == 1, (self.name, value)
            return value[0]
        return value

    def __repr__(self) -> str:
        return f"MutipleTransformer({self.name}, {self.multiple})"


class AliasTransformer(ArgumentTransformer):
    def __init__(self, name, alias) -> None:
        super().__init__(name)
        assert isinstance(alias, dict) or callable(alias)
        self.alias = alias

    @property
    def enabled(self):
        return self.alias

    def _apply_to_value_once(self, value):
        if isinstance(value, (tuple, list)):
            return [self.apply_to_value(v) for v in value]

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

    def valid_with_multiple(self, multiple_transformer):
        mult = multiple_transformer.multiple
        if mult is False and isinstance(self.alias, dict):
            for k, v in self.alias.items():
                if isinstance(v, (tuple, list)):
                    raise ValueError(
                        f"Mismatch for '{self.name}' with alias={self.alias} and mutiple={mult}."
                    )

    def apply_to_value(self, value):
        old = object()
        while old != value:
            old = value
            value = self._apply_to_value_once(old)
        return value

    def __repr__(self) -> str:
        return f"Alias({self.name}, {self.alias})"


class FormatTransformer(ArgumentTransformer):
    def __init__(self, name, type=None) -> None:
        super().__init__(name)
        self.type = type

    @property
    def enabled(self):
        return not self.type is None

    def apply_to_value(self, value):
        if isinstance(value, (list, tuple)):
            return [self.type(v) for v in value]
        return self.type(value)

    def __repr__(self) -> str:
        txt = "Format("
        txt += f"{self.name}"
        if self.type is not None:
            txt += f",{self.type}"
        txt += ")"
        return txt


class NormalizeTransformer(ArgumentTransformer):
    def __init__(self, name, values) -> None:
        super().__init__(name)
        self.values = values

        from climetlab.normalize import _find_normaliser

        self.norm = _find_normaliser(values)

    def apply_to_value(self, value):
        return self.norm(value)

    def __repr__(self) -> str:
        return f"{self.norm} ({self.values})"


class AvailabilityTransformer(Transformer):
    def __init__(self, availability=None, _availability=None) -> None:
        self.availability = availability
        if _availability is None:
            _availability = Availability(availability)
        self._availability = _availability

    def _apply_to_kwargs(self, kwargs):
        LOG.debug("Checking availability for %s", kwargs)

        def stringify(s):
            if isinstance(s, (list, tuple)):
                return [stringify(x) for x in s]

            if isinstance(s, dict):
                r = {}
                for k, v in s.items():
                    r[k] = stringify(v)
                return r

            return str(s)

        self._availability.check(stringify(kwargs))
        return kwargs

    def __repr__(self) -> str:
        txt = "Availability:"
        for l in self._availability.tree().split("\n"):
            if l:
                txt += "\n    " + l
        return txt
