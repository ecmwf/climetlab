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


class Transformer:
    def valid_with_multiple(self, multiple_transformer):
        pass


class ArgumentTransformer(Transformer):
    def __init__(self, name) -> None:
        self.name = name

    def apply_to_kwargs(self, kwargs):
        if self.name not in kwargs:
            return kwargs
        kwargs[self.name] = self.apply_to_value(kwargs[self.name])
        return kwargs

    def apply_to_value(self, value):
        raise NotImplementedError()


class MultipleTransformer(ArgumentTransformer):
    def __init__(self, name, multiple) -> None:
        super().__init__(name)
        assert multiple in [True, False]
        self.multiple = multiple

    def apply_to_value(self, value):
        is_list = isinstance(value, (list, tuple))
        if self.multiple and not is_list:
            return [value]
        if not self.multiple and is_list:
            assert len(value) == 1, (self.name, value)
            return value[0]
        return value


class AliasTransformer(ArgumentTransformer):
    def __init__(self, name, data) -> None:
        super().__init__(name)
        assert isinstance(data, dict) or callable(data)
        self.data = data

    def _apply_to_value_once(self, value):
        if isinstance(value, (tuple, list)):
            return [self.apply_to_value(v) for v in value]

        if callable(self.data):
            return self.data(value)

        if isinstance(self.data, dict):
            try:
                return self.data[value]
            except KeyError:  # No alias for this value
                pass
            except TypeError:  # if value is not hashable
                pass
            return value

        assert False, (self.name, self.data)

    def valid_with_multiple(self, multiple_transformer):
        mult = multiple_transformer.multiple
        if mult is False and isinstance(self.data, dict):
            for k, v in self.data.items():
                if isinstance(v, (tuple, list)):
                    raise ValueError(
                        f"Mismatch for '{self.name}' with alias={self.data} and mutiple={mult}."
                    )

    def apply_to_value(self, value):
        old = object()
        while old != value:
            old = value
            value = self._apply_to_value_once(old)
        return value
