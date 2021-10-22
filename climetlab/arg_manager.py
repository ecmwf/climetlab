# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from climetlab.utils.args import add_default_values_and_kwargs

LOG = logging.getLogger(__name__)


class Action:
    def __init__(self) -> None:
        self.actions_stack = None

    def merge_with(self, old):
        pass

    def destroy(self):
        pass


class ActionsStack:
    def __init__(self, func, actions=None):
        self.func = func
        if actions is None:
            actions = []
        self._actions = actions

    def remove(self, a):
        self._actions.remove(a)

    def append_list(self, actions):
        for c in actions:
            self.append(c)

    def append(self, action):

        for old in self._actions:
            action.merge_with(old)

        self._actions.append(action)
        action.actions_stack = self

    def __call__(self, args, kwargs):
        for c in self._actions:
            args, kwargs = c(args, kwargs, self.func)
        return args, kwargs

    def __str__(self):
        s = "ArgManager\n"
        for i, a in enumerate(self._actions):
            s += f"  {i}: {a}\n"
        return s


class NormalizerAction(Action):
    def __init__(self, key, values=None, **kwargs):
        from climetlab.normalize import _find_normaliser

        values = kwargs.pop("values", values)

        for k, v in kwargs.items():
            assert not k.startswith("_")

        alias = kwargs.pop("alias", {})
        assert (
            not kwargs
        ), f"Unknown argument(s): {', '.join([str(k) for k in kwargs.keys()])}"

        norm = _find_normaliser(values)

        if alias:
            if not hasattr(norm, "alias"):
                raise ValueError(f"Normalizer {norm} does not accept argument alias")
            norm.alias = alias

        from climetlab.normalize import _find_normaliser

        self.key = key
        self.norm = norm
        super().__init__()

    def destroy(self):
        self.actions_stack.remove(self)

    def merge_with_normalizer(self, norm):
        if self.key == norm.key:
            LOG.warning(f"Multiple normalizer for arg {self.key}")
            self.destroy()

    def merge_with_availability(self, action):
        av = action.availability
        for value in av.unique_values()[self.key]:
            _value = self.norm(value)
            if _value != value and _value != [value]:
                raise ValueError(
                    f"Mismatch between availability and normalizer {_value} != {value}"
                )

    def merge_with(self, old):
        old.merge_with_normalizer(self)

    def __call__(self, args, kwargs, func):
        if self.key in kwargs:
            kwargs[self.key] = self.norm(kwargs[self.key])

        return args, kwargs


class FixKwargsAction(Action):
    def __call__(self, args, kwargs, func):
        return add_default_values_and_kwargs(args, kwargs, func)

    def merge_with_normalizer(self, norm):
        pass

    def merge_with_availability(self, a):
        pass

    def merge_with(self, a):
        pass


class AvailabilityAction(Action):
    def __init__(self, availability):
        self.availability = availability
        super().__init__()

    def __call__(self, args, kwargs, func):
        LOG.debug("Checking availability for %s", kwargs)
        self.availability.check(**kwargs)
        return args, kwargs

    def merge_with_normalizer(self, norm):
        norm.merge_with_availability(self)

    def merge_with_availability(self, a):
        raise NotImplementedError("Multiple availabilities were provided")

    def merge_with(self, old):
        old.merge_with_availability(self)
