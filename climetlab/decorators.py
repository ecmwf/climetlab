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
        manager = InputManager(decorators=decorators)
        LOG.debug("Built manager: %s", manager)

        @wraps(unwrapped)
        def newfunc(*args, **kwargs):

            LOG.debug("Applying decorator stack to: %s %s", args, kwargs)

            from climetlab.arguments.args_kwargs import ArgsKwargs

            args_kwargs = ArgsKwargs(args, kwargs, func=unwrapped)
            args_kwargs = add_default_values_and_kwargs(args_kwargs)
            if args_kwargs.args:
                raise ValueError(f"There should not be anything in {args_kwargs.args}")

            args_kwargs.kwargs = manager.apply_to_kwargs(args_kwargs.kwargs)

            args_kwargs.ensure_positionals()

            args, kwargs = args_kwargs.args, args_kwargs.kwargs

            LOG.debug("CALLING func %s %s", args, kwargs)
            return unwrapped(*args, **kwargs)

        newfunc._climetlab_decorators = decorators

        return newfunc

    def get_aliases(self):
        return None

    def get_multiple(self):
        return None

    def get_format(self):
        return None

    def get_type(self):
        return None


class normalize(Decorator):
    def __init__(
        self,
        name,
        values=None,
        alias=None,
        multiple=None,
        type=None,
        format=None,
    ):
        self.name = name
        self.values = values
        self.alias = alias
        self.multiple = multiple
        self.type = type
        self.format = format

        self.parse_values(values)

    def parse_values(self, values):
        from climetlab.normalize import (
            BoundingBoxNormaliser,
            DateNormaliser,
            EnumNormaliser,
            VariableNormaliser,
        )

        NORMALISERS = {
            "enum": EnumNormaliser,
            "enum-list": EnumNormaliser,
            "date-list": DateNormaliser,
            "date": DateNormaliser,
            "variable-list": VariableNormaliser,
            "bounding-box": BoundingBoxNormaliser,
            "bbox": BoundingBoxNormaliser,
        }

        if callable(values):
            self.norm = values
            return

        if isinstance(values, (tuple, list)):
            self.values = list(values)
            if self.multiple is None:
                if isinstance(values, tuple):
                    self.multiple = False
                if isinstance(values, list):
                    self.multiple = True
            self.norm = EnumNormaliser(values)

        assert isinstance(values, str), values
        if values.endswith("-list"):
            self.multiple = True

        m = re.match(r"(.+)\((.+)\)", values)

        if not m:
            self.norm = NORMALISERS[values]()
            return

        args = m.group(2).split(",")
        name = m.group(1)
        self.norm = NORMALISERS[name](*args)
        return

    def visit(self, manager):
        manager.parameters[self.name].append(self)

    def get_values(self, name):
        assert self.name == name
        return self.values

    def get_multiple(self):
        return self.multiple

    def get_format(self):
        return self.format

    def get_type(self):
        return self.type

    def get_format(self):
        return self.format


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
