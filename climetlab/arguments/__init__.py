# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

from climetlab.decorators import Decorator, availability
from climetlab.utils.availability import Availability

from .transformers import (
    AliasTransformer,
    AvailabilityTransformer,
    FormatTransformer,
    MultipleTransformer,
    NormalizeTransformer,
)

LOG = logging.getLogger(__name__)

KEYWORDS = ["alias", "normalize", "availability", "multiple", "format", "type"]


class Block:
    def apply_to_one_value(self, name, value):
        for t in self.transformers:
            kwargs = t.apply_to_kwargs(kwargs)
        return kwargs


class MultipleBlock(Block):
    key = "multiple"


class AliasBlock(Block):
    key = "alias"


class NormBlock(Block):
    needs = "normalizer"


class AvailabilityBlock(Block):
    needs = "availability"


class Argument:
    def __init__(
        self, name, values=None, alias=None, multiple=None, format=None, type=None
    ):
        self.name = name

        self._data = {k: None for k in KEYWORDS}
        self._decorators = []

        if isinstance(values, tuple):
            self._data["multiple"] = False
        elif isinstance(values, list):
            self._data["multiple"] = True

        if alias:
            self._data["alias"] = alias

        # self.validate()

    def add_deco(self, deco):
        print("Adding decorator ", deco)
        if deco.name != self.name:
            return
        self._decorators.append(deco)

    def merge_decorators(self):
        self._data["alias"] = self.merged_alias("alias")
        self._data["multiple"] = self.merged_multiple("multiple")
        self._data["format"] = self.merged_format("format")
        self._data["type"] = self.merged_type("type")

    def merged_format(self, key):
        return self.merged_generic(key)

    def merged_type(self, key):
        return self.merged_generic(key)

    def merged_generic(self, key):
        many = self._decorators
        out = None
        if not many:
            return out
        for deco in many:
            x = deco.get(key)
            if x is None:
                continue
            if out is None:
                out = x
                continue
            if x != out:
                raise Exception(f"Inconsistent values for {key}")
        return out

    def merged_alias(self, key):
        many = self._decorators
        out = {}
        if not many:
            return out
        for deco in many:
            v = deco.get(key)
            if v is None:
                continue
            out.update(v)
        return out

    def merged_multiple(self, key):
        many = self._decorators
        out = None
        if not many:
            return out
        for deco in many:
            x = deco.get("multiple")
            if x is None:
                continue
            if out is None:
                out = x
                continue
            if x != out:
                raise Exception(f"Inconsistent values for {key}")
        if not out is None:
            return out

        for deco in many:
            values = deco.get("values")
            if isinstance(values, tuple):
                x = False
            if isinstance(values, list):
                x = True
            if x is None:
                continue
            if out is None:
                out = x
                continue
            if x != out:
                raise Exception(f"Inconsistent implicit values for {key}")
        if not out is None:
            return out
        return None

    def __repr__(self) -> str:
        txt = "-- " + self.name + "\n"
        for k, v in self._data.items():
            if v is None:
                continue
            txt += f"    {k}={v}\n"
        txt += "  decorators:\n"
        for d in self._decorators:
            txt += f"    {d}\n"
        return txt

    def validate(self):
        pass
        # if self.count_decorators("multiple") > 1:
        #    LOG.warn(f"Multiple value for 'multiple' provided for {self.name}")

        # if self.count_decorators("alias") > 1:
        #    LOG.warn(f"Multiple value for 'alias' provided for {self.name}")

    def apply_to_kwargs(self, kwargs):
        return Arguments([self]).apply_to_kwargs(kwargs)


class Arguments:
    def __init__(
        self,
        arguments=None,
        decorators=None,
        availability=None,
    ):
        self.decorators = []
        self._blocks = dict(
            alias=AliasBlock(),
            norm=NormBlock(),
            availability=AvailabilityBlock(),
            multiple=MultipleBlock(),
        )
        self.pipeline = []

        self.availabilities = []
        if availability:
            self.availabilities = [availability]

        if not arguments:
            arguments = []

        assert all(isinstance(a, Argument) for a in arguments), arguments
        self.arguments = arguments

        if decorators:
            assert all(isinstance(a, Decorator) for a in decorators), decorators
            self.add_decorators(decorators)

        self.build_pipeline()

    def build_pipeline(self):
        for a in self.arguments:
            transform = AliasTransformer(a.name, a._data["alias"])
            self.pipeline.append(transform)

        for a in self.arguments:
            transform = FormatTransformer(a.name, a._data["type"])
            self.pipeline.append(transform)

        for av in self.availabilities:
            transform = AvailabilityTransformer(_availability=av)
            self.pipeline.append(transform)

        for a in self.arguments:
            transform = FormatTransformer(a.name, a._data["format"])
            self.pipeline.append(transform)

        for a in self.arguments:
            transform = MultipleTransformer(a.name, a._data["multiple"])
            self.pipeline.append(transform)

        print("----------------------------")
        print("Pipeline built")
        for t in self.pipeline:
            if t.enabled:
                print(" ", t)
        print("----------------------------")

    def __repr__(self) -> str:
        txt = f"ARGUMENTS:[\n"
        txt += f" availability >>>\n"
        if self.availabilities:
            txt += f"{self.availabilities}<<<"
        else:
            txt += "None<<<"
        txt += "\n"
        for a in self.arguments:
            txt += f"  {a}\n"
        txt += "]"
        txt += f"Pipeline:[\n"
        for t in self.pipeline:
            txt += f"  {t}\n"
        txt += "]"
        return txt

    def get(self, name, auto_create=True):
        for a in self.arguments:
            if a.name == name:
                return a
        a = Argument(name)
        self.arguments.append(a)
        return a

    def get_decorator(self, kind):
        for deco in self.decorators:
            if deco.kind == kind:
                return deco

    def get_decorators(self, kind):
        lst = []
        for deco in self.decorators:
            if deco.kind == kind:
                lst.append(deco)
        return lst

    def _get_new_names(self):
        names = [deco.name for deco in self.decorators if deco.name]
        for av in self.availabilities:
            names += list(av.unique_values().keys())
        names = set(names)
        old = set([a.name for a in self.arguments])
        return list(names - old)

    def add_decorators(self, decorators):
        self.decorators += decorators

        for deco in self.get_decorators("availability"):
            av = deco.get("availability")
            self.availabilities.append(Availability(av))

        self.arguments += [Argument(name) for name in self._get_new_names()]

        for a in self.arguments:
            for deco in decorators:
                a.add_deco(deco)
            a.validate()
            a.merge_decorators()

        print("Arguments built:-------------------------")
        print(self)

        # self.validate_arguments()

    def validate_blocks(self):
        if self._alias and self.multiple:
            self._alias[0].valid_with_multiple(self._multiple[0])

    def validate(self):
        for a in self.arguments:
            a.validate()
        # availability.validate

    # for deco in self.get_decorators(self._decorators, "normalize"):
    #     arg = self.get(deco.name)
    #     if "alias" in deco.init_kwargs:
    #         arg.add_alias(alias=deco.init_kwargs["alias"], _who=1)

    # def _set_normalize(self):
    #     for deco in self.get_decorators(self._decorators, "normalize"):
    #         arg = self.get(deco.name)
    #         arg.add_normalize(values=deco.init_kwargs["values"], _who=0)
    #     for deco in self.get_decorators(self._decorators, "availability"):
    #         av = Availability(deco.init_kwargs["availability"])
    #         for name, values in av.unique_values().items():
    #             arg = self.get(name)
    #             arg.add_normalize(values=values, _who=-1)

    def apply_to_kwargs(self, kwargs):
        print("Apply pipeline")
        print(f"   kwargs: {kwargs}")
        for t in self.pipeline:
            if t.enabled:
                print(f" - applying {t}")
                kwargs = t.__call__(kwargs)
                print(f"   kwargs: {kwargs}")
        print(kwargs)

        return kwargs
