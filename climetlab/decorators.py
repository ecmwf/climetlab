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
import re
import threading
from functools import wraps

from climetlab.utils import load_json_or_yaml
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


OPTIONS = {
    "date": ("format",),
    "date-list": ("format",),
    "bounding-box": ("format",),
    "bbox": ("format",),
    "variable": ("convention",),
    "variable-list": ("convention",),
}


class normalize(Decorator):
    def __init__(
        self,
        name,
        values=None,
        **kwargs,
    ):
        assert name is None or isinstance(name, str)
        self.name = name

        if isinstance(values, str):
            assert (
                kwargs.get("type") is None
            ), f"Cannot mix values={values} and type={kwargs.get('type')}"
            if "(" in values:
                m = re.match(r"(.+)\((.+)\)", values)
                type = m.group(1)
                args = m.group(2).split(",")
            else:
                type = values
                args = []

            # len(args) <= len(options)
            if args:
                for name, value in zip(OPTIONS[type], args):
                    kwargs[name] = value
            kwargs["type"] = type
        else:
            kwargs["values"] = values

        if "aliases" in kwargs and isinstance(kwargs["aliases"], str):
            _, ext = os.path.splitext(kwargs["aliases"])
            if ext in (".json", ".yaml", ".yml"):
                path = kwargs["aliases"]
                if not os.path.isabs(path):
                    caller = os.path.dirname(inspect.stack()[1].filename)
                    path = os.path.join(caller, path)
                kwargs["aliases"] = load_json_or_yaml(path)

        self.kwargs = kwargs

    def register(self, manager):
        manager.register_normalize(self)


class availability(Decorator):
    is_availability = True

    def __init__(self, availability, **kwargs):
        if isinstance(availability, str):
            if not os.path.isabs(availability):
                caller = os.path.dirname(inspect.stack()[1].filename)
                availability = os.path.join(caller, availability)

        self.availability = Availability(availability, **kwargs)

    def register(self, manager):
        manager.register_availability(self)
