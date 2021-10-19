# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging

LOG = logging.getLogger(__name__)


class ArgsManager:
    def __init__(self, *args, **kwargs):
        self.commands = []

    def disable(self):
        self.commands = []

    def append(self, cmd):
        self.commands.append(cmd)

    def apply(self, args, kwargs):
        for cmd in self.commands:
            args, kwargs = cmd.apply(args, kwargs)
        return args, kwargs

    def __str__(self):
        s = "ArgManager\n"
        for i, cmd in enumerate(self.commands):
            s += f"  {i}: {cmd}\n"
        return s


class ArgsCmd:
    def apply(self, args, kwargs):
        return args, kwargs


class NormalizerWrapper(ArgsCmd):
    def __init__(self, key, norm):
        self.key = key
        self.norm = norm

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
