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
            from climetlab.arg_manager import ActionsStack

            action_stack = ActionsStack(func)
            func._args_manager = action_stack
        return action_stack

    def register_to_action_stack(self, action_stack):
        action_stack.append(self)

    def __call__(self, func):
        action_stack = self._get_action_stack(func)
        self.register_to_action_stack(action_stack)

        @wraps(func)
        def inner(*args, **kwargs):
            LOG.debug("Applying arg_manager: %s", action_stack)
            print("CALLING manager", args, kwargs)
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

    def apply_to_args_kwargs(self, args_kwargs):
        kwargs = args_kwargs.kwargs
        if self.key in kwargs:
            value = kwargs[self.key]
            if isinstance(self.data, dict):
                while value in self.data:
                    value = self.data[value]
                kwargs[self.key] = value

            elif callable(self.data):
                kwargs[self.key] = self.data(value)
            else:
                raise Exception

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
