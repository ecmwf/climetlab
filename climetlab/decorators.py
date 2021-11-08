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

from climetlab.arguments.climetlab_types import infer_type

# from climetlab.arguments.guess import guess_type_list
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


class Decorator:

    is_availability = False

    def __call__(self, func):
        from climetlab.arguments import InputManager

        if not callable(func):
            manager = InputManager(decorators=[self])
            return manager.apply_to_value(func)

        decorators = [self]

        def unwrap(f):
            if not hasattr(f, "_climetlab_decorators"):
                return f
            return unwrap(f.__wrapped__)

        unwrapped = unwrap(func)

        if hasattr(func, "_climetlab_decorators"):
            decorators = decorators + func._climetlab_decorators

        manager = InputManager(decorators=decorators)

        @wraps(unwrapped)
        def newfunc(*args, **kwargs):
            args, kwargs = manager.apply_to_arg_kwargs(args, kwargs, func=unwrapped)
            return unwrapped(*args, **kwargs)

        newfunc._climetlab_decorators = decorators

        return newfunc


class normalize(Decorator):
    def __init__(
        self,
        name,
        values=None,
        aliases=None,
        multiple=None,
        type=None,
        format=None,
        optional=False,
    ):
        assert name is None or isinstance(name, str)

        self.name = name
        self.aliases = aliases
        self.multiple = multiple
        self.format = format
        self.optional = optional

        options = {}
        self.cml_type = infer_type(values, type, multiple, options)

        # In case the infer_type changes anynthing, e.g. format
        for k, v in options.items():
            setattr(self, k, v)

        # TODO: check if still needed
        if self.format is None:
            if self.cml_type is str:
                self.format = str

    def visit(self, manager):
        manager.parameters[self.name].append(self)

    def get_values(self):
        return self.values


class availability(Decorator):
    is_availability = True

    def __init__(self, availability):
        if isinstance(availability, str):
            if not os.path.isabs(availability):
                caller = os.path.dirname(inspect.stack()[1].filename)
                availability = os.path.join(caller, availability)

        self.availability = Availability(availability)

    def visit(self, manager):
        for name in self.availability.unique_values().keys():
            manager.parameters[name].append(self)
        manager.availabilities.append(self.availability)

    def get_values(self, name):
        return self.availability.unique_values()[name]

    def gess_cml_type(self, name):
        # TODO: get type from availability values
        return None
