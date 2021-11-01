# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

from climetlab.decorators import Decorator
from climetlab.utils.availability import Availability

from .argument import Argument
from .transformers import (
    AliasTransformer,
    AvailabilityTransformer,
    FormatTransformer,
    MultipleTransformer,
    NormalizeTransformer,
)

LOG = logging.getLogger(__name__)

KEYWORDS = ["alias", "normalize", "availability", "multiple", "format", "type"]


class InputManager:
    def __init__(
        self,
        decorators,
    ):
        self.decorators = decorators
        self.pipeline = []

        self.availabilities = []

        self.names = set()
        for decorator in self.decorators:
            decorator.visit(self)

        self.arguments = [Argument(name) for name in self.names]


        self.build_pipeline()

    def build_pipeline(self):
        print("InputManager :-------------------------")
        print(self)

        for a in self.arguments:
            transform = AliasTransformer(a.name, a._data["alias"])
            self.pipeline.append(transform)

        for a in self.arguments:
            transform = NormalizeTransformer(a.name, a._data["values"])
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
        txt = "ARGUMENTS:[\n"
        txt += " availability >>>\n"
        if self.availabilities:
            txt += f"{self.availabilities}<<<"
        else:
            txt += "None<<<"
        txt += "\n"
        for a in self.arguments:
            txt += f"  {a}\n"
        txt += "]"
        txt += "Pipeline:[\n"
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
        assert all(isinstance(a, Decorator) for a in decorators), decorators

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

        # self.validate_arguments()

        # if self._alias and self.multiple:
        #     self._alias[0].valid_with_multiple(self._multiple[0])

    # def validate(self):
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


def normaliser(*args, **kwargs):
    return Argument("no-name", *args, **kwargs)
