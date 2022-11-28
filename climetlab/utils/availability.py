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

import io
import itertools
import json
import os

import yaml

from climetlab.utils.factorise import Tree, factorise

from .humanize import dict_to_human, list_to_human


def _tidy_dict(query):
    result = dict()
    for k, v in query.items():
        if v is None:
            continue
        result[k] = v
    return result


def load_str(avail):
    try:
        return json.loads(avail)
    except json.decoder.JSONDecodeError:
        return yaml.safe_load(avail)


def load_json(avail):
    with open(avail) as f:
        return json.loads(f.read())


def load_yaml(avail):
    with open(avail) as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


CONFIG_LOADERS = {
    ".json": load_json,
    ".yaml": load_yaml,
}


class Availability:
    def __init__(self, avail, intervals=None, parser=None):
        if not isinstance(avail, Tree):
            if isinstance(avail, str):
                config_loader = load_json
                if len(avail) > 5:
                    config_loader = CONFIG_LOADERS.get(avail[-5:], load_str)
                    avail = config_loader(avail)

            if parser is not None:
                avail = [parser(item) for item in avail]

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
        last = -1
        for line in input:
            line = line.rstrip()
            cnt = 0
            while len(line) > 0 and line[0] == " ":
                line = line[1:]
                cnt += 1
            if cnt <= last:
                requests.append(as_dict(",".join(stack)))
            while len(stack) > cnt:
                stack.pop()
            stack.append(line)
            last = cnt

        if stack:
            requests.append(as_dict(",".join(stack)))

        return cls(requests, intervals)

    def _repr_html_(self):
        return "<hr><pre>{}</pre><hr>".format(self.tree())

    def select(self, *args, **kwargs):
        return Availability(self._tree.select(*args, **kwargs))

    def missing(self, *args, **kwargs):
        # assert kwargs.keys() == self.unique_values().keys(), "kwargs must contain all dimensions"
        return Availability(self._tree.missing(*args, **kwargs))

    def check(self, _kwargs=None, **kwargs):
        assert _kwargs is None or not kwargs

        if _kwargs is not None and not kwargs:
            assert isinstance(_kwargs, dict)
            kwargs = _kwargs

        if self.count(kwargs):
            return

        reasons = []

        #         u = self.unique_values()
        #         for k, v in kwargs.items():
        #             if v is None:
        #                 continue
        #             if k not in u:
        #                 reasons.append(f"Unknown key {k}")
        #                 continue
        #             if v not in u[k]:
        #                 reasons.append(f"Invalid value for {k}: {v} must be in {u[k]}")
        #                 continue

        query = kwargs

        if not reasons:

            def iterate_request(r):
                yield from (
                    dict(zip(r.keys(), x)) for x in itertools.product(*r.values())
                )

            def build(x):
                # if isinstance(x, (list, tuple)):
                #    return [None] + list(x)
                return [None, x]

            r = {k: build(v) for k, v in query.items()}

            lst = []
            for i in iterate_request(r):
                if self.count(i) == 0:
                    i = _tidy_dict(i)
                    lst.append((abs(len(i) - 2), i))

            lst = sorted(lst, key=lambda x: x[0])

            if len(lst) > 0:
                for x in lst:
                    if x[0] == lst[0][0]:
                        ii = dict_to_human(x[1])
                        reasons.append(f"invalid combination ({ii})")

        raise ValueError(f"{list_to_human(reasons)}.")

    def __len__(self):
        return self.count()

    def __getattr__(self, name):
        return getattr(self._tree, name)


if __name__ == "__main__":
    for n in Availability.from_mars_list("mars.list.tree").iterate():
        print(n)
