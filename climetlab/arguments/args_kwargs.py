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

LOG = logging.getLogger(__name__)


class ArgsKwargs:
    def __init__(self, args, kwargs, func=None):
        assert isinstance(kwargs, dict)
        assert isinstance(args, (list, tuple))
        args = list(args)

        self.args = args
        self.kwargs = kwargs
        self.func = func

        self.positionals_only = []
        self.defaults = {}

    def add_default_values_and_kwargs(self):
        new_args = []
        new_kwargs = {}

        sig = inspect.signature(self.func)
        bnd = sig.bind(*self.args, **self.kwargs)
        parameters_names = list(sig.parameters)

        bnd.apply_defaults()

        new_kwargs.update(bnd.kwargs)

        # TODO: delete this (sic!)
        #
        # if parameters_names[0] == "self":
        #     # func must be method. Store first argument and skip it latter
        #     LOG.debug('Skipping first parameter because it is called "self"')
        #     new_args = new_args + [self.args.pop(0)]
        #     parameters_names.pop(0)

        for name in parameters_names:
            param = sig.parameters[name]

            if param.default != inspect.Parameter.empty:
                self.defaults[name] = param.default

            if param.kind is param.VAR_POSITIONAL:  # param is *args
                new_args = new_args + self.args
                continue

            if param.kind is param.VAR_KEYWORD:  # param is **kwargs
                new_kwargs.update(bnd.arguments[name])
                continue

            if param.kind is param.POSITIONAL_ONLY:
                # new_args = new_args + [bnd.arguments[name]]
                # continue
                self.positionals_only.append(name)

            new_kwargs[name] = bnd.arguments[name]

        LOG.debug("Fixed input arguments args=%s, kwargs=%s", new_args, new_kwargs)

        self.args = new_args
        self.kwargs = new_kwargs

    def ensure_positionals_only(self):
        """Move positional arguments from self.kwargs into self.args"""
        for name in self.positionals_only:
            value = self.kwargs.pop(name)
            self.args.append(value)
