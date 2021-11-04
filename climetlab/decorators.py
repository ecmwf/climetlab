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

from climetlab.arguments.climetlab_types import _find_cml_type
from climetlab.arguments.guess import guess_type_list
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

    def get_aliases(self):
        return None

    def get_multiple(self):
        return None

    def get_cml_type(self, name):
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
        if name is not None:
            assert isinstance(name, str)

        self._type_from_values = None

        self.name = name
        self.alias = alias
        self.multiple = multiple
        self.type = type
        self.format = format

        self.parse_values(values)
        print(f"Parsed values {values}. type = {self.type}")

        if self.format is None:
            if self.type is str:
                self.format = str

    def parse_values(self, values):
        if not values:
            self.values = None
            return

        if isinstance(values, (tuple, list)):
            self.values = list(values)
            self._type_guessed_from_values = guess_type_list(values)
            return

        assert isinstance(values, str), values
        self.values = None

        if "(" in values:
            m = re.match(r"(.+)\((.+)\)", values)
            cml_type_str = m.group(1)
            args = m.group(2).split(",")
        else:
            cml_type_str = values
            args = []

        self._type_from_values = cml_type_str
        self._cml_type_args = args

    def visit(self, manager):
        manager.parameters[self.name].append(self)

    def get_values(self, name=None):
        return self.values

    def get_multiple(self):
        if self.cml_type:
            return self.cml_type.multiple
        return self.multiple

    def get_aliases(self):
        return self.alias

    @property
    def cml_type(self):
        return self.get_cml_type()

    def get_cml_type(self):
        # explicitely given as a string in values='type(...)'
        if self._type_from_values:
            type = _find_cml_type(self._type_from_values, self.multiple)
            return type(*self._cml_type_args)

        # explicitely given in type=
        if self.type:
            type = _find_cml_type(self.type, self.multiple)
            return type()

        # infer from values
        if self._type_guessed_from_values:
            type = _find_cml_type(self._type_guessed_from_values, self.multiple)
            return type()

        return None


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

    def get_cml_type(self, name):
        return None
