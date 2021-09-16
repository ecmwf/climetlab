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
import io
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

    @classmethod
    def from_mars_list(cls, tree, intervals=None):
        if os.path.exists(tree):
            input = open(tree)
        else:
            input = io.StringIO(tree)

        def as_dict(s):
            r = {}
            for a in s.split(","):
                p, v = a.split("=")
                r[p] = v.split("/")
            return r

        requests = []
        stack = []
        last = 0
        for line in input:
            line = line.rstrip()
            cnt = 0
            while len(line) > 0 and line[0] == " ":
                line = line[1:]
                cnt += 1
            if cnt <= last and stack:
                requests.append(as_dict(",".join(stack)))
            while len(stack) <= cnt:
                stack.append(None)
            stack[cnt] = line
            last = cnt

        if stack:
            requests.append(as_dict(",".join(stack)))

        return cls(requests, intervals)

    def _repr_html_(self):
        return "<hr><pre>{}</pre><hr>".format(self.tree())

    def select(self, *args, **kwargs):
        return Availability(self._tree.select(*args, **kwargs))

    def missing(self, *args, **kwargs):
        return Availability(self._tree.missing(*args, **kwargs))

    def check(self, **kwargs):
        if self.count(**kwargs):
            return

        reasons = []

        u = self.unique_values()
        for k, v in kwargs.items():
            if v is None:
                continue
            if k not in u:
                reasons.append(f"Unknown key {k}")
                continue
            if v not in u[k]:
                reasons.append(f"Invalid value for {k}: {v} must be in {u[k]}")
                continue

        if not reasons:
            lst = {}
            for k, v in kwargs.items():
                if v is None:
                    continue
                lst[k] = v
            reasons.append(f"Invalid combination {lst}")

        raise ValueError(f"No data ({reasons}).")

    def __len__(self):
        return self.count()

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


if __name__ == "__main__":
    for n in Availability.from_mars_list("mars.list.tree").iterate():
        print(n)
