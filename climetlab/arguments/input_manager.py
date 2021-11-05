# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging
from collections import defaultdict

from .argument import Argument
from .transformers import Action, AvailabilityChecker

LOG = logging.getLogger(__name__)


class InputManager:
    def __init__(
        self,
        decorators,
    ):
        self.decorators = decorators
        self._pipeline = None

        self.availabilities = []

        LOG.debug("Building arguments from decorators:\n %s", decorators)
        self.parameters = defaultdict(list)
        for decorator in self.decorators:
            decorator.visit(self)

        self.arguments = [
            Argument(name, decorators) for name, decorators in self.parameters.items()
        ]

        LOG.debug("Built manager: %s", self)

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = []
            self.build_pipeline()
            for t in self._pipeline:
                if not isinstance(t, Action):
                    raise f"Unknown action: {t}"
        return self._pipeline

    def build_pipeline(self):
        print("Building...")

        for a in self.arguments:
            a.add_type_transformers(self._pipeline)

        for a in self.arguments:
            a.add_alias_transformers(self._pipeline)

        for a in self.arguments:
            a.add_enum_transformers(self._pipeline)

        for availability in self.availabilities:
            transform = AvailabilityChecker(availability)
            self._pipeline.append(transform)

        for a in self.arguments:
            a.add_format_transformers(self._pipeline)

        print("----------------------------")
        print("Pipeline built")
        for t in self._pipeline:
            print(" ", t)
        print("----------------------------")

    def apply_to_kwargs(self, kwargs):
        print(f"Apply pipeline to kwargs: {kwargs}")
        for t in self.pipeline:
            if t.name:
                print(f" - {t.name}: apply {t}.")
            else:
                print(f" - apply {t}.")

            kwargs = t.execute(kwargs)
            print(f"       kwargs: {kwargs}")
        print(f"Applied pipeline: {kwargs}")
        print()

        return kwargs

    def apply_to_value(self, value):
        for t in self.pipeline:
            value = t.__call__(value)
        return value

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
        if self._pipeline is None:
            txt += "Pipeline[not-ready]"
        else:
            txt += "Pipeline:[\n"
            for t in self._pipeline:
                txt += f"  {t}\n"
            txt += "]"
        return txt

    def apply_to_arg_kwargs(self, args, kwargs, func):
        from climetlab.arguments.args_kwargs import ArgsKwargs

        args_kwargs = ArgsKwargs(args, kwargs, func=func)
        args_kwargs.add_default_values_and_kwargs()
        if args_kwargs.args:
            raise ValueError(f"There should not be anything in {args_kwargs.args}")

        LOG.debug("Applying decorator stack to: %s %s", args, kwargs)
        args_kwargs.kwargs = self.apply_to_kwargs(args_kwargs.kwargs)

        args_kwargs.ensure_positionals()

        args, kwargs = args_kwargs.args, args_kwargs.kwargs

        LOG.debug("CALLING func %s %s", args, kwargs)
        return args, kwargs


def normaliser(*args, **kwargs):
    return Argument("no-name", *args, **kwargs)
