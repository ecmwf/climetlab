# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from climetlab.decorators import (
    AvailabilityDecorator,
    Decorator,
    FixKwargsDecorator,
    NormalizeDecorator,
)
from climetlab.utils.args import ArgsKwargs

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
        self._availability = None
        self._av_values = {}

    def remove(self, a):
        self._compiled = False
        self._actions.remove(a)

    def append(self, action):
        assert isinstance(action, Decorator), action
        self._compiled = False

        assert not isinstance(action, (tuple, list))

        self._actions.append(action)
        action.actions_stack = self

        if isinstance(action, NormalizeDecorator):
            if action.key not in self._normalizers:
                self._normalizers[action.key] = []
            self._normalizers[action.key].append(action)

        if isinstance(action, AvailabilityDecorator):
            if self._availability:
                raise NotImplementedError("Multiple availabilities were provided")
            self._availablity = action
            self._av_values = action.availability.unique_values()

    def get_norms(self, key):
        return self._normalizers.get(key, [])

    def get_keys(self):
        keys = []
        for a in self._actions:
            if isinstance(a, NormalizeDecorator):
                keys.append(a.key)
            if isinstance(a, AvailabilityDecorator):
                keys += list(a.availability.unique_values().keys())
        return list(set(keys))

    def compile(self):
        new_actions = []

        new_actions.append(FixKwargsDecorator())

        av_values = self._av_values
        availability = self._availability

        for key in self.get_keys():
            norms = self.get_norms(key)
            av_values_key = av_values.get(key, None)

            assert norms or av_values_key, (norms, av_values_key)

            if len(norms) > 1:
                LOG.warning(f"Multiple normalizers for arg {key}")
                norms = [norms[-1]]  # choose only one

            if not norms:
                values = av_values_key
                assert av_values_key, values
                norm = NormalizeDecorator(key, values=av_values_key)
                new_actions.append(norm)
                continue

            assert len(norms) == 1, norms
            norm = norms[0]

            if not av_values_key:
                new_actions.append(norm)
                continue

            for value in av_values_key:
                _value = norm.norm.normalize_one_value(value)
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
        for a in self._actions:
            args_kwargs = a.apply_to_args_kwargs(args_kwargs)

        args_kwargs.ensure_positionals()
        args = args_kwargs.args
        kwargs = args_kwargs.kwargs

        return tuple(args), kwargs

    def __str__(self):
        s = "ArgManager\n"
        for i, a in enumerate(self._actions):
            s += f"  {i}: {a}\n"
        return s
