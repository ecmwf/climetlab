# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import inspect
import threading

from climetlab.normalisers import NORMALISERS


class parameters:
    def __init__(self, **kwargs):
        self.types = dict()
        for k, v in kwargs.items():
            if isinstance(v, str):
                v = v.split(":")
            if hasattr(v[0], "normalise"):
                assert len(v) == 1, v
                self.types[k] = v[0]
            else:
                self.types[k] = NORMALISERS[v[0]](*v[1:])

    def __call__(self, func):

        spec = inspect.getfullargspec(func)

        def wrapped(*args, **kwargs):

            request = dict()
            request.update(kwargs)

            for p, a in zip(spec.args, args):
                request[p] = a

            request = self.normalise(request)
            return func(**request)

        wrapped.__name__ = func.__name__

        return wrapped

    def normalise(self, request):
        result = dict(**request)

        for k, v in self.types.items():
            if k in request:
                n = v.normalise(request[k])
                if n is not None:
                    result[k] = n

        return result


def dict_args(func):
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

    wrapped.__name__ = func.__name__

    return wrapped


LOCK = threading.RLock()


def locked(func):
    def wrapped(*args, **kwargs):
        with LOCK:
            return func(*args, **kwargs)

    wrapped.__name__ = func.__name__

    return wrapped
