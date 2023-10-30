# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import re

LOG = logging.getLogger(__name__)


class Remapping(dict):
    # inherit from dict to make it serialisable

    def __init__(self, remapping):
        super().__init__(remapping)

        self.lists = {}
        for k, v in remapping.items():
            if isinstance(v, str):
                v = re.split(r"\{([^}]*)\}", v)
            self.lists[k] = v

    def __call__(self, func):
        if not self:
            return func

        class CustomJoiner:
            def format_name(self, x):
                return func(x)

            def format_string(self, x):
                return str(x)

            def join(self, args):
                return "".join(str(x) for x in args)

        joiner = CustomJoiner()

        def wrapped(name):
            return self.substitute(name, joiner)

        return wrapped

    def substitute(self, name, joiner):
        if name in self.lists:
            if callable(self.lists[name]):
                return self.lists[name]()

            lst = []
            for i, bit in enumerate(self.lists[name]):
                if i % 2:
                    p = joiner.format_name(bit)
                    if p is not None:
                        lst.append(p)
                    else:
                        lst = lst[:-1]
                else:
                    lst.append(joiner.format_string(bit))
            return joiner.join(lst)
        return joiner.format_name(name)

    def as_dict(self):
        return dict(self)


def _build_remapping(mapping):
    if mapping is None:
        return Remapping({})

    if not isinstance(mapping, Remapping) and isinstance(mapping, dict):
        return Remapping(mapping)

    return mapping


class Patch(dict):
    # inherit from dict to make it serialisable

    def __init__(self, proc, name, patch):
        self.proc = proc
        self.name = name

        if isinstance(patch, dict):
            self.patch = lambda x: patch.get(x, x)
        elif isinstance(patch, (int, bool, float, str)) or patch is None:
            self.patch = lambda x: patch
        else:
            assert callable(patch)
            self.patch = patch

        # For JSON, we simply forward to the remapping
        super().__init__(proc.as_dict())

    def __call__(self, func):
        next = self.proc(func)

        def wrapped(name):
            result = next(name)
            if name == self.name:
                result = self.patch(result)
            return result

        return wrapped
        # assert False, (name, self.proc, self.name, self.patch)

    def as_dict(self):
        return dict(self)


def build_remapping(mapping, patches=None):
    result = _build_remapping(mapping)
    if patches:
        for k, v in patches.items():
            result = Patch(result, k, v)
    return result


def normalize_order_by(*args, **kwargs):
    _kwargs = {}
    for a in args:
        if a is None:
            continue
        if isinstance(a, dict):
            _kwargs.update(a)
            continue
        if isinstance(a, str):
            _kwargs[a] = "ascending"
            continue
        if isinstance(a, (list, tuple)):
            if not all(isinstance(k, str) for k in a):
                _kwargs.update(normalize_order_by(*a))
            else:
                for k in a:
                    _kwargs[k] = "ascending"
            continue

        raise ValueError(f"Unsupported argument {a} of type {type(a)}")

    _kwargs.update(kwargs)

    for k, v in _kwargs.items():
        if not (
            v is None
            or callable(v)
            or isinstance(v, (list, tuple, set))
            or v in ["ascending", "descending"]
        ):
            raise ValueError(f"Unsupported order: {v} of type {type(v)} for key {k}")

    return _kwargs
