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
import threading
from functools import wraps

from climetlab.utils.args import ArgsKwargs
from climetlab.utils.availability import Availability

LOG = logging.getLogger(__name__)


def dict_args(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        m = []
        p = {}
        for q in args:
            if isinstance(q, dict):
                p.update(q)
            else:
                m.append(q)
        p.update(kwargs)
        return func(*m, **p)

    return wrapped


LOCK = threading.RLock()


def locked(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        with LOCK:
            return func(*args, **kwargs)

    return wrapped


class Decorator(object):
    def __init__(self):
        self.actions_stack = None

    def _get_action_stack(self, func):
        if hasattr(func, "_args_manager"):
            action_stack = func._args_manager
            func = func.__wrapped__
        else:
            action_stack = DecoratorStack(func)
            func._args_manager = action_stack
        return action_stack

    def register_to_action_stack(self, action_stack):
        action_stack.append(self)

    def __call__(self, func):
        action_stack = self._get_action_stack(func)
        self.register_to_action_stack(action_stack)

        @wraps(func)
        def inner(*args, **kwargs):
            LOG.debug("Applying decorator stack: %s", action_stack)
            print("CALLING decorator stack", args, kwargs)
            args, kwargs = action_stack(args, kwargs)
            print("CALLING func", args, kwargs)
            return func(*args, **kwargs)

        return inner


class FixKwargsDecorator(Decorator):
    def apply_to_args_kwargs(self, args_kwargs):
        from climetlab.utils.args import add_default_values_and_kwargs

        return add_default_values_and_kwargs(args_kwargs)


class AliasDecorator(Decorator):
    def __init__(self, name, data):
        super().__init__()
        assert isinstance(data, dict) or callable(data), data

        self.data = data

        self.key = name

    def _resolve_alias(self, value):
        if isinstance(value, (tuple, list)):
            return [self._resolve_alias(v) for v in value]

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

        assert False, (self.key, self.data)

    def apply_to_args_kwargs(self, args_kwargs):
        kwargs = args_kwargs.kwargs

        if self.key not in kwargs:
            return args_kwargs

        old = object()
        value = kwargs[self.key]
        while old != value:
            old = value
            value = self._resolve_alias(old)
        kwargs[self.key] = value

        return args_kwargs


class NormalizeDecorator(Decorator):
    def __init__(self, name, values=None, **kwargs):
        super().__init__()

        for k, v in kwargs.items():
            assert not k.startswith("_")

        alias = kwargs.pop("alias", None)
        if alias:
            alias = AliasDecorator(name, data=alias)

        from climetlab.normalize import _find_normaliser

        values = kwargs.pop("values", values)
        norm = _find_normaliser(values, **kwargs)

        # if hasattr(norm, "alias"):
        #    norm.alias = alias
        #    raise ValueError(f"Normalizer {norm} does not accept argument alias")

        self.alias = alias
        self.key = name
        self.norm = norm

    def register_to_action_stack(self, action_stack):
        if self.alias:
            assert isinstance(self.alias, AliasDecorator)
            action_stack.append(self.alias)
        action_stack.append(self)

    def apply_to_args_kwargs(self, args_kwargs):
        kwargs = args_kwargs.kwargs
        if self.key in kwargs:
            kwargs[self.key] = self.norm(kwargs[self.key])

        return args_kwargs


class AvailabilityDecorator(Decorator):
    def __init__(self, avail):
        super().__init__()

        if isinstance(avail, str):
            if not os.path.isabs(avail):
                caller = os.path.dirname(inspect.stack()[1].filename)
                avail = os.path.join(caller, avail)

        avail = Availability(avail)
        self.availability = avail
        super().__init__()

    def apply_to_args_kwargs(self, args_kwargs):
        LOG.debug("Checking availability for %s", args_kwargs.kwargs)
        self.availability.check(**args_kwargs.kwargs)
        return args_kwargs


_fix_kwargs = FixKwargsDecorator
normalize = NormalizeDecorator
availability = AvailabilityDecorator
alias = AliasDecorator


class DecoratorStack:
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

    def get_aliases(self, key=None):
        for a in self._actions:
            if not isinstance(a, AliasDecorator):
                continue
            if key is not None and a.key != key:
                continue
            yield a

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
        LOG.debug("Compiling decorator stack: %s", self._actions)

        new_actions.append(FixKwargsDecorator())

        for a in self.get_aliases():
            new_actions.append(a)

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
        LOG.debug("Compiled decorator stack: %s", self._actions)

    def __call__(self, args, kwargs):
        if not self._compiled:
            self.compile()

        args_kwargs = ArgsKwargs(args, kwargs, func=self.func)
        print(self._actions)
        for a in self._actions:
            print(f"Applying decorator {a}")
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
