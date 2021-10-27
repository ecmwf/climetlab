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
import weakref
from functools import wraps

from climetlab.arguments.args_kwargs import ArgsKwargs
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
    def __init__(self, kind, **kwargs):
        self.arguments = None
        self.kind = kind
        self.init_kwargs = kwargs
        if "name" in kwargs:
            self.name = kwargs["name"]

    def unwrap(self, f):
        decorators = [self]
        while hasattr(f, "__wrapped__") and hasattr(f, "_climetlab_deco"):
            decorators = [f._climetlab_deco] + decorators
            f = f.__wrapped__
        return f, decorators

    def __call__(self, func):
        from climetlab.arguments import Arguments
        from climetlab.arguments.args_kwargs import add_default_values_and_kwargs

        unwrapped, decorators = self.unwrap(func)

        @wraps(unwrapped)
        def newfunc(*args, **kwargs):
            if self.arguments is None:
                self.arguments = Arguments(decorators)

            LOG.debug("Applying decorator stack to: %s %s", args, kwargs)

            args_kwargs = ArgsKwargs(args, kwargs, func=unwrapped)
            args_kwargs = add_default_values_and_kwargs(args_kwargs)
            if args_kwargs.args:
                raise ValueError(f"There should not be anything in {args_kwargs.args}")

            args_kwargs.kwargs = self.arguments.apply_to_kwargs(args_kwargs.kwargs)

            args_kwargs.ensure_positionals()

            args, kwargs = args_kwargs.args, args_kwargs.kwargs

            LOG.debug("CALLING func %s %s", args, kwargs)
            return unwrapped(*args, **kwargs)

        newfunc._climetlab_deco = self

        return newfunc


class FixKwargsDecorator(Decorator):
    def apply_to_args_kwargs(self, args_kwargs):
        from climetlab.arguments.args_kwargs import add_default_values_and_kwargs

        return add_default_values_and_kwargs(args_kwargs)


class MultipleDecorator(Decorator):
    def __init__(self, name, multiple):
        assert multiple in [True, False]
        super().__init__("multiple", name=name, multiple=multiple)


class AliasDecorator(Decorator):
    def __init__(self, name, alias):
        assert isinstance(alias, dict) or callable(alias), alias
        super().__init__("alias", name=name, alias=alias)


class NormalizeDecorator(Decorator):
    def __init__(self, name, values=None, alias=None, multiple=None):
        super().__init__(
            "normalize",
            name=name,
            values=values,
            alias=alias,
            multiple=multiple,
        )
        return

        if alias:
            self.alias = AliasDecorator(name, data=alias)
        else:
            self.alias = None

        def _multiple():
            if "multiple" in kwargs:
                return kwargs["multiple"]
            if isinstance(values, list):
                return True
            if isinstance(values, tuple):
                return False

            return False

        from climetlab.normalize import _find_normaliser

        values = kwargs.pop("values", values)
        norm = _find_normaliser(values, **kwargs)

        self.key = name
        self.norm = norm

    def apply_to_args_kwargs(self, ak: ArgsKwargs):
        kwargs = ak.kwargs
        if self.key in kwargs:
            kwargs[self.key] = self.norm(kwargs[self.key])

        return ak

    def __repr__(self):
        txt = "NormalizeDecorator("
        txt += self.key
        if self.alias:
            txt += f", alias={self.alias}"
        txt += f", norm={self.norm}"
        txt += ")"
        return txt


class AvailabilityDecorator(Decorator):
    def __init__(self, avail):

        if isinstance(avail, str):
            if not os.path.isabs(avail):
                caller = os.path.dirname(inspect.stack()[1].filename)
                avail = os.path.join(caller, avail)

        avail = Availability(avail)
        self.availability = avail

    def apply_to_args_kwargs(self, args_kwargs):
        LOG.debug("Checking availability for %s", args_kwargs.kwargs)

        def stringify(s):
            if isinstance(s, (list, tuple)):
                return [stringify(x) for x in s]

            if isinstance(s, dict):
                r = {}
                for k, v in s.items():
                    r[k] = stringify(v)
                return r

            return str(s)

        self.availability.check(stringify(args_kwargs.kwargs))
        return args_kwargs

    def __repr__(self):
        txt = "AvailabilityDecorator(\n"
        txt += f"{self.availability.tree()}"
        txt += ")"
        return txt


_fix_kwargs = FixKwargsDecorator
normalize = NormalizeDecorator
availability = AvailabilityDecorator
alias = AliasDecorator


class DecoratorStack:
    def __init__(self, func, decorators=None):
        self.func = func
        if decorators is None:
            decorators = []
        self.decorators = decorators
        self.arguments = None

    def append(self, decorator):
        assert isinstance(decorator, Decorator), decorator
        self.decorators.append(decorator)

    def __str__(self):
        s = "DecoratorStack(\n"
        for i, a in enumerate(self.decorators):
            s += f"  decorator {i}: {a}\n"
        s += ")"
        return s


class Old:
    def get_norms(self, key):
        if key not in self._normalizers:
            return None

        norms = self._normalizers[key]
        if len(norms) > 1:
            LOG.warning(f"Multiple normalizers for arg {key}")
        return norms[-1]

    def get_aliases(self, key=None):
        for a in self.get_decorators(AliasDecorator, key):
            yield a

    def get_multiples(self, key=None):
        for a in self.get_decorators(MultipleDecorator, key):
            yield a

    def get_decorators(self, klass, key=None):
        for a in self._actions:
            if not isinstance(a, klass):
                continue
            if key is not None and a.key != key:
                continue
            yield a

    def get_availability(self):
        availabilities = [
            a for a in self._actions if isinstance(a, AvailabilityDecorator)
        ]
        if len(availabilities) > 1:
            raise NotImplementedError("Multiple availabilities were provided")
        if availabilities:
            return availabilities[0]
        return None

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
        print("A", self)

        new_actions.append(FixKwargsDecorator())

        for a in self.get_aliases():
            new_actions.append(a)

        availability_deco = self.get_availability()
        if availability_deco:
            av_values = availability_deco.availability.unique_values()
        else:
            av_values = {}

        for key in self.get_keys():
            norm_deco = self.get_norms(key)
            av_values_key = av_values.get(key, None)

            assert norm_deco or av_values_key, (norm_deco, av_values_key)

            if norm_deco is None:
                values = av_values_key
                assert av_values_key, values
                norm_deco = NormalizeDecorator(key, values=av_values_key)
                new_actions.append(norm_deco)
                continue

            if av_values_key is None:
                new_actions.append(norm_deco)
                continue

            for value in av_values_key:
                _value = norm_deco.norm.normalize_one_value(value)
                if _value != value and _value != [value]:
                    raise ValueError(
                        (
                            "Mismatch between availability and normalizer "
                            f"{str(_value)}({type(_value)}) != {value}({type(value)})"
                        )
                    )

            new_actions.append(norm_deco)

        if availability_deco:
            new_actions.append(availability_deco)

        for a in self.get_multiples():
            new_actions.append(a)

        self._actions = new_actions
        self._compiled = True
        LOG.debug("Compiled decorator stack: %s", self._actions)
        print("Z", self)

    def __call__(self, args, kwargs):
        if not self._compiled:
            self.compile()

        args_kwargs = ArgsKwargs(args, kwargs, func=self.func)
        for a in self._actions:
            args_kwargs = a.apply_to_args_kwargs(args_kwargs)

        args_kwargs.ensure_positionals()
        args = args_kwargs.args
        kwargs = args_kwargs.kwargs

        return tuple(args), kwargs
