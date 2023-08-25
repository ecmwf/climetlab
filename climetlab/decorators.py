# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import functools
import inspect
import logging
import os
import re
import threading

from climetlab.utils import load_json_or_yaml
from climetlab.utils.availability import Availability

LOG = logging.getLogger(__name__)


def dict_args(func):
    @functools.wraps(func)
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
    @functools.wraps(func)
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

        @functools.wraps(unwrapped)
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


def normalize_grib_keys(f):
    f = alias_argument("levelist", ["level", "levellist"])(f)
    f = alias_argument("levtype", ["leveltype"])(f)
    f = alias_argument("param", ["variable", "parameter"])(f)
    f = alias_argument("number", ["realization", "realisation"])(f)
    f = alias_argument("class", ["klass", "class_"])(f)
    return f


def _normalize_time_as_tuple(time, type):
    if isinstance(time, str):
        time = (time,)
    return tuple(_normalize_time(t, type) for t in time)


def _normalize_time(time, type):
    assert type in (int, str), type

    if time is None or time == all:
        return time

    if isinstance(time, list):
        return [_normalize_time(t, type) for t in time]
    if isinstance(time, tuple):
        return tuple([_normalize_time(t, type) for t in time])

    try:
        time = int(time)
    except ValueError:
        return time

    if time % 100:  # not multiple of 100
        time = time * 100

    assert time <= 2400, time
    assert time >= 0, time

    if type is str:
        return f"{time:04d}"
    assert isinstance(time, int)
    return time


def _normalize_expver(expver):
    if isinstance(expver, str):
        return expver
    assert isinstance(expver, int)
    return f"{expver:04}"


def _normalize_expver_as_tuple(expver):
    if isinstance(expver, (int, str)):
        expver = _normalize_expver(expver)
        expver = (expver,)
    lst = []
    for x in expver:
        if not isinstance(x, str):
            x = "%04d" % x
        lst.append(x)
    return tuple(lst)


def normalize_grib_key_values(kwargs, accept_none=True, as_tuple=False):
    def f(**kwargs):
        return kwargs

    f = normalize_grib_keys(f)
    f = normalize("param", "variable-list(mars)")(f)
    f = normalize("date", "date-list(%Y%m%d)")(f)
    f = normalize("area", "bounding-box(list)")(f)
    f = normalize("levelist", "int-list")(f)
    kwargs = f(**kwargs)

    if "time" in kwargs:
        kwargs["time"] = {False: _normalize_time, True: _normalize_time_as_tuple}[
            as_tuple
        ](kwargs["time"], int)
    if "expver" in kwargs:
        kwargs["expver"] = {False: _normalize_expver, True: _normalize_expver_as_tuple}[
            as_tuple
        ](kwargs["expver"])

    return kwargs


class alias_argument(Decorator):
    def __init__(
        self,
        target=None,
        aliases=None,
        **kwargs,
    ):
        """target: actual argument name in the function to decorate.
        aliases: str or list of str to create aliases to target.
        """
        if target is not None:
            assert aliases is not None
            assert not kwargs
            kwargs = {target: aliases}

        for k, v in kwargs.items():
            if isinstance(v, (list, tuple)):
                continue
            if isinstance(v, str):
                kwargs[k] = [v]
                continue
            if isinstance(v, dict):
                raise ValueError(
                    (
                        "Error: alias_argument is expecting a list or str."
                        f" You may be looking for: @normalize(aliases={kwargs})"
                    )
                )
            raise ValueError(f"Wrong alias list for '{k}':{v}")

        self.kwargs = kwargs

        # check for duplicate aliases
        for k, v in self.kwargs.items():
            for k_, v_ in self.kwargs.items():
                if k == k_:
                    continue
                intersection = set(v).intersection(set(v_))
                if intersection:
                    raise ValueError(
                        f"Error: alias_argument cannot alias '{list(intersection)[0]}' to '{k}' and '{k_}'"
                    )

    def register(self, manager):
        manager.register_alias_argument(self)


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


def cached_method(method):
    name = f"_{method.__name__}"

    @functools.wraps(method)
    def wrapped(self):
        if getattr(self, name, None) is None:
            setattr(self, name, method(self))
        return getattr(self, name)

    return wrapped
