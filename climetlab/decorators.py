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
import os
import threading
from functools import wraps

from climetlab.arg_manager import ArgsManager, AvailabilityWrapper, NormalizerWrapper
from climetlab.utils.availability import Availability

LOG = logging.getLogger(__name__)


def dict_args(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        m = []
        p = {}
        for q in args:
            if isinstance(q, dict):
                p.update(q)
            else:
                m.append(q)
        p.update(kwargs)
        return func(*m, **p)

    return wrapped


LOCK = threading.RLock()


def locked(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        with LOCK:
            return func(*args, **kwargs)

    return wrapped


def availability(avail):

    if isinstance(avail, str):
        if not os.path.isabs(avail):
            caller = os.path.dirname(inspect.stack()[1].filename)
            avail = os.path.join(caller, avail)

    avail = Availability(avail)

    wrapper = AvailabilityWrapper(avail)

    def outer(func):
        args_manager = ArgsManager.from_func(func, disable=True)
        args_manager.append(wrapper)

        @wraps(func)
        def inner(*args, **kwargs):
            # TODO: implement avail.check here with *args also?
            _, kwargs = args_manager.apply((), kwargs)
            return func(*args, **kwargs)

        inner._args_manager = args_manager

        return inner

    return outer


def normalize(name, values=None, **kwargs):
    from climetlab.normalize import _find_normaliser

    values = kwargs.pop("values", values)

    for k, v in kwargs.items():
        assert not k.startswith("_")

    norm = _find_normaliser(values)

    alias = kwargs.pop("alias", {})
    if alias:
        if not hasattr(norm, "alias"):
            raise ValueError(f"Normalizer {norm} does not accept argument alias")
        norm.alias = alias

    args_wrapper = NormalizerWrapper(name, norm)

    def wrapped(func):

        if isinstance(func, ArgsManager):
            args_manager = func
        else:
            func = wraps(func)
            args_manager = ArgsManager(func)

        args_manager.append(args_wrapper)
        LOG.debug("Normalizers: %s", args_manager)

        return args_manager


    return wrapped  


def normalize_args(**kwargs):
    from climetlab.normalize import _find_normaliser

    args_wrappers = []

    availability = kwargs.pop("_availability", None)
    if availability is not None:
        args_wrappers.append(AvailabilityWrapper(availability))

    alias = kwargs.pop("_alias", {})

    for k, v in kwargs.items():
        norm = _find_normaliser(v)
        if hasattr(norm, "alias"):
            norm.alias = alias.get(k, None)
        args_wrappers.append(NormalizerWrapper(k, norm))

    def outer(func):

        args_manager = ArgsManager.from_func(func, disable=True)
        args_manager.append(args_wrappers)
        LOG.debug("Normalizers: %s", args_manager)

        @wraps(func)
        def inner(*args, **kwargs):
            provided = inspect.getcallargs(func, *args, **kwargs)
            for name, param in inspect.signature(func).parameters.items():
                # See https://docs.python.org/3.5/library/inspect.html#inspect.signature
                assert param.kind is not param.VAR_POSITIONAL
                if param.kind is param.VAR_KEYWORD:
                    provided.update(provided.pop(name, {}))

            # if hasattr(func, '__self__'):

            # TODO: fix this self
            _other = provided.pop("self", None)

            args, provided = args_manager.apply((), provided)

            if _other is not None:
                provided["self"] = _other

            return func(*args, **provided)

        inner._args_manager = args_manager

        return inner

    return outer
