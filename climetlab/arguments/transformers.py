# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

LOG = logging.getLogger(__name__)


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
        data[self.name] = self.apply_to_value_or_list(data[self.name])
        return data

    def apply_to_value_or_list(self, data):
        if isinstance(data, (tuple, list)):
            return [self.apply_to_value(v) for v in data]
        return self.apply_to_value(data)

    def apply_to_value(self, value):
        raise NotImplementedError()


class MultipleTransformer(ArgumentTransformer):
    def __init__(self, name, multiple) -> None:
        super().__init__(name)
        assert multiple in [True, False, None]
        self.multiple = multiple

    def apply_to_value_or_list(self, value):
        is_list = isinstance(value, (list, tuple))
        if self.multiple and not is_list:
            return [value]
        if not self.multiple and is_list:
            if len(value) > 1:
                raise ValueError(f"Cannot provide non-multiple value for {value}.")
            return value[0]
        return value

    def __repr__(self) -> str:
        return f"MutipleTransformer({self.name}, {self.multiple})"


class AliasTransformer(ArgumentTransformer):
    def __init__(self, name, alias) -> None:
        super().__init__(name)
        assert isinstance(alias, dict) or callable(alias) or alias is None
        self.alias = alias

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
    def __init__(self, name, format=None) -> None:
        super().__init__(name)
        self.format = format

    def apply_to_value(self, value):
        return self.format(value)

    def __repr__(self) -> str:
        txt = "Format("
        txt += f"{self.name}"
        if self.format is not None:
            txt += f",{self.format}"
        txt += ")"
        return txt


class TypeTransformer(ArgumentTransformer):
    def __init__(self, name, type=None) -> None:
        super().__init__(name)
        self.type = type
        from climetlab.utils.bbox import to_bounding_box
        from climetlab.utils.conventions import normalise_string
        from climetlab.utils.dates import to_date_list
        def to_int(x):
            print(x)
            print(x)
            print(x)
            print(x)
            print(x)
            return int(x)
        TYPES = {
            int: to_int,
            str: str,
            float: float,
            None: _identity,
            "int": to_int,
            "str": str,
            "float": float,
            "date": to_date_list,
            "bbox": to_bounding_box,
        }
        self.transform = TYPES[type]

    def apply_to_value(self, value):
        print('v',value, self.transform)
        return self.transform(value)

    def __repr__(self) -> str:
        txt = "Type("
        txt += f"{self.name}"
        if self.type is not None:
            txt += f",{self.type}"
        txt += ")"
        return txt


class NormalizeTransformer(ArgumentTransformer):
    def __init__(self, name, norm, type=None) -> None:
        super().__init__(name)
        assert callable(norm), norm
        self.norm = norm
        self.type = type

    def apply_to_value(self, value):
        return self.norm(value)

    def __repr__(self) -> str:
        return f"Normalize({self.name}, {self.norm}, type={self.type})"


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
