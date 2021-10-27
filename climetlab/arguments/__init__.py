# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

from climetlab.arguments.args_kwargs import ArgsKwargs

from .transformers import AliasTransformer, MultipleTransformer

LOG = logging.getLogger(__name__)

LOG.setLevel(logging.DEBUG)


class Argument:
    def __init__(
        self, name, values=None, alias=None, multiple=None, format=None, type=None
    ):
        self.name = name

        self.values = None
        self.alias = None
        self.multiple = None

        self._alias = []
        self._multiple = []

        if isinstance(self.values, tuple):
            self.add_multiple(False)
        elif isinstance(self.values, list):
            self.add_multiple(True)
        self.add_multiple(multiple)

        self.add_alias(alias)
        self.validate()

    def validate(self):
        if len(self._multiple) > 1:
            LOG.warn(f"Multiple value for 'multiple' provided for {self.name}")
            self._multiple = [self._multiple[0]]

        if len(self._alias) > 1:
            LOG.warn(
                f"Multiple value for 'alias' provided for {self.name} use only one"
            )
            self._alias = [self._alias[0]]  # TODO merge aliases

        for a in self._alias:
            a.valid_with_multiple(self._multiple[0])

    def apply_alias_to_kwargs(self, kwargs):
        for t in self._alias:
            kwargs = t.apply_to_kwargs(kwargs)

    def apply_multiple_to_kwargs(self, kwargs):
        for t in self._multiple:
            kwargs = t.apply_to_kwargs(kwargs)
        return kwargs

    def add_multiple(self, multiple):
        if multiple is None:
            return
        self._multiple.append(MultipleTransformer(self.name, multiple))

    def add_alias(self, alias):
        if alias is None:
            return
        self._alias.append(AliasTransformer(self.name, alias))


class Arguments:
    def __init__(
        self,
        input=None,
        availability=None,
    ):
        from climetlab.decorators import Decorator

        self.availability = availability
        self.arguments = []

        if not input:
            input = []
        assert isinstance(input, (list, tuple))

        if isinstance(input[0], Argument):
            assert [isinstance(a, Argument) for a in input], input
            self.arguments = input
            return

        if isinstance(input[0], Decorator):
            assert [isinstance(a, Decorator) for a in input], input
            self._decorators = input
            self._build_from_decorators()
            return

        assert False, input

    def get(self, name, auto_create=True):
        for a in self.arguments:
            if a.name == name:
                return a
        a = Argument(name)
        self.arguments.append(a)
        return a

    def _build_from_decorators(self):
        self._set_alias()
        # self._set_type()
        self._set_multiple()
        self._set_normalize()
        self._set_availability()

    def _set_multiple(self):
        for deco in self.get_decorators(self._decorators, "multiple"):
            arg = self.get(deco.name)
            arg.add_multiple(multiple=deco.init_kwargs["multiple"])

    def _set_alias(self):
        for deco in self.get_decorators(self._decorators, "alias"):
            arg = self.get(deco.name)
            arg.add_alias(alias=deco.init_kwargs["alias"])

    def _set_normalize(self):
        print("set-normalize todo")

    def _set_availability(self):
        availabilities = self.get_decorators(self._decorators, "availability")
        if len(availabilities) > 0 and self.availability is not None:
            raise NotImplementedError("Multiple availabilities were provided")
        if len(availabilities) > 1:
            raise NotImplementedError("Multiple availabilities were provided")
        if availabilities:
            self.availability = availabilities[0]

    def get_decorators(self, decorators, kind, name=None):
        out = []
        for d in decorators:
            if not kind is None and d.kind != kind:
                continue
            if not name is None and d.name != name:
                continue
            out.append(d)
        return out

    def apply_to_kwargs(self, kwargs):
        for a in self.arguments:
            a.apply_alias_to_kwargs(kwargs)

        # for a in self.arguments:
        #     a.apply_normalize_to_kwargs(kwargs)

        # for a in self.availability:
        #    a.apply_to_kwargs(kwargs)

        # for a in self.format:
        #    a.apply_format_to_kwargs(kwargs)

        for a in self.arguments:
            a.apply_multiple_to_kwargs(kwargs)

        return kwargs
