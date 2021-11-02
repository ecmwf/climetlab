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
from .transformers import AvailabilityTransformer, Transformer

LOG = logging.getLogger(__name__)


class InputManager:
    def __init__(
        self,
        decorators,
    ):
        self.decorators = decorators
        self.pipeline = []

        self.availabilities = []

        self.parameters = defaultdict(list)
        for decorator in self.decorators:
            decorator.visit(self)

        self.arguments = [
            Argument(name, decorators) for name, decorators in self.parameters.items()
        ]

        self.build_pipeline()

    def build_pipeline(self):
        print("InputManager :-------------------------")
        print(self)

        for a in self.arguments:
            a.add_alias_transformers(self)

        for a in self.arguments:
            a.add_normalize_transformers(self.pipeline)

        for a in self.arguments:
            a.add_type_transformers(self.pipeline)

        for availability in self.availabilities:
            transform = AvailabilityTransformer(availability)
            self.pipeline.append(transform)

        for a in self.arguments:
            a.add_format_transformers(self.pipeline)

        for a in self.arguments:
            a.add_multiple_transformers(self.pipeline)

        print("----------------------------")
        print("Pipeline built")
        for t in self.pipeline:
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

    def apply_to_kwargs(self, kwargs):
        print("Apply pipeline to kwargs: {kwargs}")
        for t in self.pipeline:
            if t.name:
                print(f" - {t.name}: apply {t}.")
            else:
                print(f" - apply {t}.")
            for t in self.pipeline:
                assert isinstance(t, Transformer), t
            kwargs = t.__call__(kwargs)
            print(f"       kwargs: {kwargs}")
        print("Applied pipeline: {kwargs}")

        return kwargs


def normaliser(*args, **kwargs):
    return Argument("no-name", *args, **kwargs)
