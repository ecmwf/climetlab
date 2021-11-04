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


def _identity(x):
    return x


class Transformer:
    name = None

    def valid_with_multiple(self, multiple_transformer):
        pass

    def __repr__(self) -> str:
        return f"{self.__class__}"


class ArgumentTransformer(Transformer):
    def __init__(self, name) -> None:
        self.name = name

    def __call__(self, data):
        data[self.name] = self.apply_to_list(data[self.name])
        return data

    def apply_to_list(self, data):
        # if self.type is None or self.type.multiple:
        #     return [self.apply_to_value(v) for v in data]
        # return self.apply_to_value(data)
        return [self.apply_to_value(v) for v in data]

    def apply_to_value(self, value):
        raise NotImplementedError()


class MultipleTransformer(ArgumentTransformer):
    def __init__(self, name, multiple) -> None:
        super().__init__(name)
        assert multiple in [True, False, None]
        self.multiple = multiple

    def apply_to_list(self, value):
        if self.multiple:
            return value
        assert isinstance(value, list), value
        assert len(value) == 1, value
        return value[0]

    def __repr__(self) -> str:
        return f"MutipleTransformer({self.name}, {self.multiple})"


class AliasTransformer(ArgumentTransformer):
    def __init__(self, name, alias, _all=None) -> None:
        super().__init__(name)
        assert isinstance(alias, dict) or callable(alias) or alias is None
        self.alias = alias
        self._all = _all

    def _apply_to_value_once(self, value):
        if value == ALL:
            assert self._all, f'Cannot find values for "ALL"'
            return self._all

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
    def __init__(self, name, type) -> None:
        super().__init__(name)
        assert isinstance(type, Type), type
        self.type = type

    def apply_to_value(self, value):
        return self.type.apply_format(value)

    def __repr__(self) -> str:
        txt = "Format("
        txt += f"{self.name}"
        if self.type is not None:
            txt += f",{self.type}"
            if hasattr(self.type, "format"):
                txt += f",{self.type.format}"
        txt += ")"
        return txt


class TypeTransformer(ArgumentTransformer):
    def __init__(self, name, type) -> None:
        super().__init__(name)
        self.type = type

    def apply_to_list(self, value):
        return self.type.cast_to_type_list(value)

    def __repr__(self) -> str:
        txt = "TypeTransformer("
        txt += f"{self.name}"
        if self.type is not None:
            txt += f",{self.type}"
        txt += ")"
        return txt


class CanonicalTransformer(ArgumentTransformer):
    def __init__(self, name, values=None, type=None) -> None:
        super().__init__(name)
        self.values = values
        self.type = type

        if values is None:
            values = []

        # if len(values) == 1 and isinstance(values[0], (list, tuple)):
        #     values = values[0]

        self.values = values

    def apply_to_value(self, value):
        print(f"       canonicalizing {value}")

        if not self.values:
            return value

        for v in self.values:
            if self.type.compare(value, v):
                return v

        self.raise_error(value)

    def raise_error(self, x):
        raise ValueError(
            f'Invalid value "{x}"({type(x)}), possible values are {self.values}'
        )

    def __repr__(self) -> str:
        return f"Canonicalize({self.name}, {self.values}, type={self.type})"


class AvailabilityTransformer(Transformer):
    def __init__(self, availability) -> None:
        self.availability = availability

    def __call__(self, kwargs):
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
