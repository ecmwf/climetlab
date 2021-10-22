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

from climetlab.arg_manager import (
    ActionsStack,
    AvailabilityAction,
    FixKwargsAction,
    NormalizerAction,
)
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


class NormalizeDecorator(object):
    def __init__(self, name, values, **kwargs):
        self.actions = [
            FixKwargsAction(),
            NormalizerAction(name, values, **kwargs),
        ]

    def __call__(self, func):
        if hasattr(func, "_args_manager"):
            action_stack = func._args_manager
            func = func.__wrapped__
        else:
            action_stack = ActionsStack(func)
            func._args_manager = action_stack

        action_stack.append_list(self.actions)

        @wraps(func)
        def inner(*args, **kwargs):
            LOG.debug("Applying arg_manager: %s", action_stack)
            args, kwargs = action_stack(args, kwargs)
            return func(*args, **kwargs)

        return inner


normalize = NormalizeDecorator


class AvailabilityDecorator(object):
    def __init__(self, avail):

        if isinstance(avail, str):
            if not os.path.isabs(avail):
                caller = os.path.dirname(inspect.stack()[1].filename)
                avail = os.path.join(caller, avail)

        avail = Availability(avail)

        self.actions = []
        self.actions.append(FixKwargsAction())

        for name, values in avail.unique_values().items():
            self.actions.append(NormalizerAction(name, values=values))

        self.actions.append(AvailabilityAction(avail))

    def __call__(self, func):
        if hasattr(func, "_args_manager"):
            action_stack = func._args_manager
            func = func.__wrapped__
        else:
            action_stack = ActionsStack(func)
            func._args_manager = action_stack

        action_stack.append_list(self.actions)

        @wraps(func)
        def inner(*args, **kwargs):
            args, kwargs = action_stack(args, kwargs)
            return func(*args, **kwargs)

        return inner


availability = AvailabilityDecorator
