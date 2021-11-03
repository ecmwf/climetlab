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
from .transformers import AvailabilityTransformer, FormatTransformer, Transformer

LOG = logging.getLogger(__name__)


class InputManager:
    def __init__(
        self,
        decorators,
    ):
        self.decorators = decorators
        self._pipeline = []

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
        return self._pipeline

    def build_pipeline(self):
        print("InputManager :-------------------------")
        print(self)

        for a in self.arguments:
            a.add_alias_transformers(self._pipeline)

        for a in self.arguments:
            a.add_normalize_transformers(self._pipeline)

        for a in self.arguments:
            a.add_type_transformers(self._pipeline)

        for availability in self.availabilities:
            transform = AvailabilityTransformer(availability)
            self._pipeline.append(transform)

        for a in self.arguments:
            a.add_format_transformers(self._pipeline)

        for a in self.arguments:
            a.add_multiple_transformers(self._pipeline)

        print("----------------------------")
        print("Pipeline built")
        for t in self._pipeline:
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
        if self._pipeline is None:
            txt += "Pipeline[not-ready]"
        else:
            txt += "Pipeline:[\n"
            for t in self._pipeline:
                txt += f"  {t}\n"
            txt += "]"
        return txt

    def apply_to_arg_kwargs(self, args, kwargs, func):
        from climetlab.arguments.args_kwargs import (
            ArgsKwargs,
            add_default_values_and_kwargs,
        )

        args_kwargs = ArgsKwargs(args, kwargs, func=func)
        args_kwargs = add_default_values_and_kwargs(args_kwargs)
        if args_kwargs.args:
            raise ValueError(f"There should not be anything in {args_kwargs.args}")

        LOG.debug("Applying decorator stack to: %s %s", args, kwargs)
        args_kwargs.kwargs = self.apply_to_kwargs(args_kwargs.kwargs)

        args_kwargs.ensure_positionals()

        args, kwargs = args_kwargs.args, args_kwargs.kwargs

        LOG.debug("CALLING func %s %s", args, kwargs)

    def apply_to_kwargs(self, kwargs):
        print("Apply pipeline to kwargs: {kwargs}")
        for t in self.pipeline:
            if t.name:
                print(f" - {t.name}: apply {t}.")
            else:
                print(f" - apply {t}.")

            for t in self.pipeline:
                if not isinstance(t, Transformer):
                    raise f"Unknown transformer: {t}"
            kwargs = t.__call__(kwargs)
            print(f"       kwargs: {kwargs}")
        print("Applied pipeline: {kwargs}")

        return kwargs

    def apply_to_value(self, value):
        for t in self.pipeline:
            value = t.__call__(value)
        return value


def normaliser(*args, **kwargs):
    return Argument("no-name", *args, **kwargs)
