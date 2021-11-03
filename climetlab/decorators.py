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

from climetlab.arguments.climetlab_types import (
    BoundingBoxType,
    DateType,
    FloatType,
    IntType,
    StrType,
    VariableType,
)
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

        self._cml_type_from_values = None

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
            if self.type is None:
                self.type = guess_type_list(values)
            if self.multiple is None:
                if isinstance(values, tuple):
                    self.multiple = False
                if isinstance(values, list):
                    self.multiple = True
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

        if cml_type_str.endswith("-list"):
            self.multiple = True

        STR_TO_CMLTYPE = {
            "enum": StrType,
            "enum-list": StrType,
            "date": DateType,
            "date-list": DateType,
            "variable": VariableType,
            "variable-list": VariableType,
            "bounding-box": BoundingBoxType,
            "bbox": BoundingBoxType,
        }
        self._cml_type_from_values = STR_TO_CMLTYPE[cml_type_str]
        self._cml_type_args = args

    def visit(self, manager):
        manager.parameters[self.name].append(self)

    def get_values(self, name=None):
        return self.values

    def get_multiple(self):
        return self.multiple

    def get_aliases(self):
        return self.alias

    def get_cml_type(self):
        import datetime

        NORMALIZE_TYPES = {
            str: StrType,
            int: IntType,
            float: FloatType,
            datetime.datetime: DateType,
        }

        # explicitely given in values='type(...)'
        type = self._cml_type_from_values
        if type:
            return type(*self._cml_type_args)

        # explicitely given in type=
        type = self.type
        if type:
            type = NORMALIZE_TYPES.get(type, None)
        if type:
            return type()

        # infer from values
        if type:
            type = guess_type_list(self.get_values())
            type = NORMALIZE_TYPES.get(type, None)
        if type:
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
