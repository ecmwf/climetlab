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

from climetlab.utils.factorise import Interval, Tree, factorise


class Availability:
    def __init__(self, avail, intervals=None):
        if not isinstance(avail, Tree):
            if isinstance(avail, str):
                with open(avail) as f:
                    avail = json.loads(f.read())
            avail = factorise(avail, intervals=intervals)
        self._tree = avail

    def _repr_html_(self):

        html = ["<hr><pre>"]
        indent = {}
        order = {}

        def V(request, depth):
            if request:
                if depth not in indent:
                    indent[depth] = len(indent) * 3
                html.append(" " * indent[depth])
                for k in sorted(request.keys()):
                    if k not in order:
                        order[k] = len(order)
                sep = ""
                for k, v in sorted(request.items(), key=lambda x: order[x[0]]):
                    html.append(sep)
                    html.append(k)
                    html.append("=")

                    if isinstance(v[0], Interval):
                        v = [str(x) for x in v]

                    if len(v) == 1:
                        html.append(v[0])
                    else:
                        html.append("[")
                        html.append(", ".join(sorted(str(x) for x in v)))
                        html.append("]")
                    sep = ", "
                html.append("\n")

        self._tree.visit(V)

        html.append("</pre><hr>")

        return "".join(x for x in html)

    def select(self, *args, **kwargs):
        return Availability(self._tree.select(*args, **kwargs))

    def count(self, *args, **kwargs):
        return self._tree.count(*args, **kwargs)

    def iterate(self, *args, **kwargs):
        return self._tree.iterate(*args, **kwargs)


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
