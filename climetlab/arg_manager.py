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

LOG = logging.getLogger(__name__)


class ArgsManager:
    def __init__(self, func, commands=None):
        # func = functools.wraps(func)
        self.func = func
        print("argmanager: ", func)
        if commands is None:
            commands = []
        self.commands = commands

    def append(self, cmd):
        if not isinstance(cmd, (list, tuple)):
            cmd = [cmd]

        for new_c in cmd:
            for c in self.commands:
                c.consistency(new_c)
            self.commands.append(new_c)

    def __call__(self, *args, **kwargs):
        for c in self.commands:
            print(f"apply {c}")
            args, kwargs = c.apply(args, kwargs)
        return args, kwargs

        print("func", self.func, args, kwargs)
        provided = inspect.getcallargs(self.func, *args, **kwargs)
        for name, param in inspect.signature(self.func).parameters.items():
            # See https://docs.python.org/3.5/library/inspect.html#inspect.signature
            assert param.kind is not param.VAR_POSITIONAL, param
            if param.kind is param.VAR_KEYWORD:
                provided.update(provided.pop(name, {}))

        assert not "self" in provided

        # if hasattr(func, '__self__'):

        # TODO: fix this self
        # _other = provided.pop("self", None)

        for c in self.commands:
            args, provided = c.apply(args, provided)

        # if _other is not None:
        #     provided["self"] = _other
        # if self.func.__self__:
        #     provided["self"] = self.func.__self__

        print("out", args, provided)
        return self.func(*args, **provided)

    def __str__(self):
        s = "ArgManager\n"
        for i, cmd in enumerate(self.commands):
            s += f"  {i}: {cmd}\n"
        return s


class ArgsCmd:
    def apply(self, args, kwargs):
        return args, kwargs

    def consistency(self, cmd):
        pass


class NormalizerWrapper(ArgsCmd):
    def __init__(self, key, norm):
        self.key = key
        self.norm = norm

    def consistency(self, cmd):
        if isinstance(cmd, NormalizerWrapper):
            # assert self.key != cmd.key, f"Multiple normalizer for {self.key}"
            if self.key == cmd.key:
                raise NotImplementedError(f"Multiple normalizer for {self.key}")

        if isinstance(cmd, AvailabilityWrapper):
            av = cmd.availability
            for value in av.unique_values()[self.key]:
                _value = self.norm(value)
                # assert _value == value or _value == [value]
                if _value != value and _value != [value]:
                    raise ValueError(
                        f"Mismatch between availability and normalizer {_value} != {value}"
                    )

    def apply(self, args, kwargs):
        # TODO: implement in args also
        if self.key not in kwargs:
            return args, kwargs

        kwargs[self.key] = self.norm(kwargs[self.key])

        return args, kwargs


class AvailabilityWrapper(ArgsCmd):
    def __init__(self, availability):
        self.availability = availability

    def apply(self, args, kwargs):
        LOG.debug("Checking availability for %s", kwargs)
        self.availability.check(**kwargs)
        return args, kwargs

    def consistency(self, cmd):
        if isinstance(cmd, AvailabilityWrapper):
            raise NotImplementedError("Multiple availabilities were provided")

        if isinstance(cmd, NormalizerWrapper):
            cmd.consistency(self)
