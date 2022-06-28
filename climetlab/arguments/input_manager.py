# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

from .argument import Argument
from .transformers import AvailabilityChecker, KwargsAliasTransformer

LOG = logging.getLogger(__name__)


class InputManager:
    def __init__(
        self,
        decorators,
    ):
        self.decorators = decorators
        self._pipeline = None
        self.alias_argument = None
        self.alias_arguments = []
        self.availabilities = []
        self.arguments = {}

    @property
    def pipeline(self):
        if self._pipeline is None:
            self.build_pipeline()
        return self._pipeline

    def register_availability(self, decorator):
        for name, values in decorator.availability.unique_values().items():
            if name not in self.arguments:
                self.arguments[name] = Argument(name)
            self.arguments[name].availability = values
        self.availabilities.append(decorator.availability)

    def register_normalize(self, decorator):
        if decorator.name not in self.arguments:
            self.arguments[decorator.name] = Argument(decorator.name)
        self.arguments[decorator.name].normalize = decorator.kwargs

    def register_alias_argument(self, decorator):
        self.alias_arguments.append(decorator)

    def build_pipeline(self):
        self._pipeline = []
        LOG.debug("Building arguments from decorators:\n %s", self.decorators)

        self.arguments = {}

        for decorator in self.decorators:
            decorator.register(self)

        self.arguments = list(self.arguments.values())

        for a in self.alias_arguments:
            transform = KwargsAliasTransformer(a)
            self._pipeline.append(transform)

        for a in self.arguments:
            a.add_alias_transformers(self._pipeline)

        for a in self.arguments:
            a.add_type_transformers(self._pipeline)

        for a in self.arguments:
            a.add_alias_transformers(self._pipeline)

        for availability in self.availabilities:
            transform = AvailabilityChecker(availability)
            self._pipeline.append(transform)

        for a in self.arguments:
            a.add_format_transformers(self._pipeline)

    def apply_to_kwargs_before_default(self, kwargs):
        LOG.debug(
            f"Apply pipeline to kwargs before resolving default values: {safe_to_str(kwargs)}"
        )
        for t in self.pipeline:
            if hasattr(t, "name"):
                LOG.debug(f" - {t.name}: apply {t}.")
            else:
                LOG.debug(f" - apply {t}.")

            kwargs = t.execute_before_default(kwargs)
            LOG.debug(f"       kwargs: {safe_to_str(kwargs)}")

        return kwargs

    def apply_to_kwargs(self, kwargs):
        LOG.debug(f"Apply pipeline to kwargs: {safe_to_str(kwargs)}")
        for t in self.pipeline:
            if hasattr(t, "name"):
                LOG.debug(f" - {t.name}: apply {t}.")
            else:
                LOG.debug(f" - apply {t}.")

            kwargs = t.execute(kwargs)
            LOG.debug(f"       kwargs: {safe_to_str(kwargs)}")

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

    def get_argument(self, name):
        for a in self.arguments:
            if a == name:
                return a
        return None

    def consolidate_defaults(self, defaults):
        for k, default in defaults.items():
            a = self.get_argument(k)
            if a:
                a.set_default(default)

    def apply_to_arg_kwargs(self, args, kwargs, func):
        from climetlab.arguments.args_kwargs import ArgsKwargs

        args_kwargs = ArgsKwargs(args, kwargs, func=func)
        LOG.debug("Applying decorator stack (before default) to: %s %s", args, kwargs)
        args_kwargs.kwargs = self.apply_to_kwargs_before_default(args_kwargs.kwargs)

        args_kwargs.add_default_values_and_kwargs()
        self.consolidate_defaults(args_kwargs.defaults)

        LOG.debug("Applying decorator stack to: %s %s", args, kwargs)
        args_kwargs.kwargs = self.apply_to_kwargs(args_kwargs.kwargs)

        args_kwargs.ensure_positionals_only()

        args, kwargs = args_kwargs.args, args_kwargs.kwargs

        LOG.debug("CALLING func %s %s", args, kwargs)
        return args, kwargs


def normaliser(*args, **kwargs):
    return Argument("no-name", *args, **kwargs)


def safe_to_str(dic):
    lst = []
    for k, v in dic.items():
        try:
            v = str(v)
        except:  # noqa: E722
            v = "..."
        lst.append(f"{k}={v}")
    return ",".join(lst)
