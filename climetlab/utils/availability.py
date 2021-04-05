#!/usr/bin/env python
#
# (C) Copyright 2021- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import functools
import inspect
import json
import os

from climetlab.utils.factorise import Tree, factorise


class Availability:
    def __init__(self, avail, intervals=None):
        if not isinstance(avail, Tree):
            if isinstance(avail, str):
                with open(avail) as f:
                    avail = json.loads(f.read())
            avail = factorise(avail, intervals=intervals)
        self._tree = avail

    def _repr_html_(self):
        return "<hr><pre>{}</pre><hr>".format(self.tree())

    def select(self, *args, **kwargs):
        return Availability(self._tree.select(*args, **kwargs))

    def missing(self, *args, **kwargs):
        return Availability(self._tree.missing(*args, **kwargs))

    def __getattr__(self, name):
        return getattr(self._tree, name)


def availability(avail):

    if isinstance(avail, str):
        if not os.path.isabs(avail):
            caller = os.path.dirname(inspect.stack()[1].filename)
            avail = os.path.join(caller, avail)

    avail = Availability(avail)

    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        return inner

    return outer
