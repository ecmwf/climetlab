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
    def __init__(self, kind, **kwargs):
        self.arguments = None
        self.kind = kind
        self.init_kwargs = kwargs

    def priority(self, key):
        return dict(
            multiple=5,
            alias=5,
            availability=1,
            normalize=2,
            format=5,
        )[self.kind]

    @property
    def name(self):
        return self.init_kwargs.get("name", None)

    def get(self, key):
        return self.init_kwargs.get(key, None)

    def has(self, key):
        return key in self.init_kwargs

    def __call__(self, func):
        from climetlab.arguments import InputManager
        from climetlab.arguments.args_kwargs import add_default_values_and_kwargs

        def unwrap(f):
            if not hasattr(f, "_climetlab_decorators"):
                return f
            return unwrap(f.__wrapped__)

        unwrapped = unwrap(func)

        decorators = [self]
        if hasattr(func, "_climetlab_decorators"):
            decorators = decorators + func._climetlab_decorators

        LOG.debug("Building arguments from decorators:\n %s", decorators)
        arguments = InputManager(decorators=decorators)
        LOG.debug("Built arguments: %s", self.arguments)

        @wraps(unwrapped)
        def newfunc(*args, **kwargs):

            LOG.debug("Applying decorator stack to: %s %s", args, kwargs)

            from climetlab.arguments.args_kwargs import ArgsKwargs

            args_kwargs = ArgsKwargs(args, kwargs, func=unwrapped)
            args_kwargs = add_default_values_and_kwargs(args_kwargs)
            if args_kwargs.args:
                raise ValueError(f"There should not be anything in {args_kwargs.args}")

            args_kwargs.kwargs = arguments.apply_to_kwargs(args_kwargs.kwargs)

            args_kwargs.ensure_positionals()

            args, kwargs = args_kwargs.args, args_kwargs.kwargs

            LOG.debug("CALLING func %s %s", args, kwargs)
            return unwrapped(*args, **kwargs)

        newfunc._climetlab_decorators = decorators

        return newfunc

    def __repr__(self):
        txt = f"{self.kind}("
        if hasattr(self, "name"):
            txt += str(self.name)
        for k, v in self.init_kwargs.items():
            if k == "name":
                continue
            if k == "availability":
                txt += f", {k}=..."
                continue
            if v is None:
                continue
            txt += f", {k}={v}"
        txt += ")"
        return txt


class _multiple(Decorator):
    def __init__(self, name, multiple):
        super().__init__("multiple", name=name, multiple=multiple)


class _alias(Decorator):
    def __init__(self, name, alias):
        super().__init__("alias", name=name, alias=alias)


class normalize(Decorator):
    def __init__(self, name, values=None, alias=None, multiple=None, type=None):
        super().__init__(
            "normalize",
            name=name,
            values=values,
            alias=alias,
            multiple=multiple,
            type=type,
        )


class availability(Decorator):
    def __init__(self, availability):
        if isinstance(availability, str):
            if not os.path.isabs(availability):
                caller = os.path.dirname(inspect.stack()[1].filename)
                availability = os.path.join(caller, availability)

        super().__init__("availability", availability=availability)
