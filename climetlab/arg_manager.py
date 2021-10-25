# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from climetlab.utils.args import ArgsKwargs, add_default_values_and_kwargs

LOG = logging.getLogger(__name__)


class Action:
    def __init__(self) -> None:
        self.actions_stack = None


class ActionsStack:
    def __init__(self, func, actions=None):
        self.func = func
        if actions is None:
            actions = []
        self._actions = actions
        self._compiled = False
        self._normalizers = {}

    def remove(self, a):
        self._compiled = False
        self._actions.remove(a)

    def append_list(self, actions):
        self._compiled = False
        for c in actions:
            self.append(c)

    def append(self, action):
        self._compiled = False

        assert not isinstance(action, (tuple, list))

        self._actions.append(action)
        action.actions_stack = self

        if isinstance(action, NormalizerAction):
            if action.key not in self._normalizers:
                self._normalizers[action.key] = []
            self._normalizers[action.key].append(action)

    def get_norms(self, key):
        return self._normalizers.get(key, [])

    def compile(self):
        new_actions = []

        new_actions.append(FixKwargsAction())

        availabilities = list(
            filter(lambda a: isinstance(a, AvailabilityAction), self._actions)
        )

        if len(availabilities) > 1:
            raise NotImplementedError("Multiple availabilities were provided")

        av_values = {}
        availability = None
        if availabilities:
            availability = availabilities[0]
            av_values = availability.availability.unique_values()

        def find_keys(_actions):
            keys = []
            for a in _actions:
                if isinstance(a, NormalizerAction):
                    keys.append(a.key)
                if isinstance(a, AvailabilityAction):
                    keys += list(a.availability.unique_values().keys())
            return list(set(keys))

        for key in find_keys(self._actions):
            norms = self.get_norms(key)
            av_values_key = av_values.get(key, None)

            assert norms or av_values_key, (norms, av_values_key)

            if len(norms) > 1:
                LOG.warning(f"Multiple normalizers for arg {key}")
                norms = [norms[0]]  # choose only one

            if not norms:
                values = availability.availability.unique_values()[key]
                assert values, values
                norm = NormalizerAction(key, values=values)
                new_actions.append(norm)
                continue

            assert len(norms) == 1, norms
            norm = norms[0]

            if not av_values_key:
                new_actions.append(norm)
                continue

            for value in av_values_key:
                _value = norm.norm(value)
                if _value != value and _value != [value]:
                    raise ValueError(
                        f"Mismatch between availability and normalizer {str(_value)}({type(_value)}) != {value}({type(value)})"
                    )

                new_actions.append(norm)

        if availability:
            new_actions.append(availability)

        self._actions = new_actions
        self._compiled = True

    def __call__(self, args, kwargs):
        # if not self._compiled:
        self.compile()

        args_kwargs = ArgsKwargs(args, kwargs, func=self.func)
        for c in self._actions:
            args_kwargs = c(args_kwargs)

        args_kwargs.ensure_positionals()
        args = args_kwargs.args
        kwargs = args_kwargs.kwargs

        return tuple(args), kwargs

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

        norm = _find_normaliser(values, **kwargs)

        if alias:
            if not hasattr(norm, "alias"):
                raise ValueError(f"Normalizer {norm} does not accept argument alias")
            norm.alias = alias

        self.key = key
        self.norm = norm
        super().__init__()

    def __call__(self, args_kwargs):
        kwargs = args_kwargs.kwargs
        if self.key in kwargs:
            kwargs[self.key] = self.norm(kwargs[self.key])

        return args_kwargs


class FixKwargsAction(Action):
    def __call__(self, args_kwargs):
        return add_default_values_and_kwargs(args_kwargs)


class AvailabilityAction(Action):
    def __init__(self, availability):
        self.availability = availability
        super().__init__()

    def __call__(self, args_kwargs):
        LOG.debug("Checking availability for %s", args_kwargs.kwargs)
        self.availability.check(**args_kwargs.kwargs)
        return args_kwargs
