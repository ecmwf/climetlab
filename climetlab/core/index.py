# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import functools
import hashlib
import json
import logging
from abc import abstractmethod

from climetlab.decorators import alias_argument, normalize
from climetlab.sources import Source

LOG = logging.getLogger(__name__)


class OrderOrSelection:
    def __init__(self, *args, **kwargs):
        """Parse args and kwargs to build a dictionary in self.order"""
        self.dic = {}

        for arg in args:
            res_ok = self.parse_arg(arg)
            if res_ok is False:
                raise ValueError(f"Invalid argument of type({type(arg)}): {arg}")

        self.parse_kwargs(kwargs)

    @alias_argument("levelist", ["level"])
    @alias_argument("param", ["variable", "parameter"])
    @alias_argument("number", ["realization", "realisation"])
    @alias_argument("class", "klass")
    def normalize_naming(self, **kwargs):
        return kwargs

    def parse_kwargs(self, kwargs):
        """Parse a dictionary of keywords arguments"""
        kwargs = self.normalize_naming(**kwargs)
        for k, v in kwargs.items():
            self.parse_kwarg(k, v)

    def parse_kwarg(self, k, v):
        """Parse one keywords argument"""
        raise NotImplementedError

    def parse_arg(self, arg):
        """Parse one argument
        Returns True of argument is a dict and has been parsed.
        """
        if arg is None:
            return True
        if isinstance(arg, dict):
            self.parse_kwargs(arg)
            return True
        return False

    def __str__(self):
        return f"{self.__class__.__name__}({self.dic})"

    @property
    def is_empty(self):
        return not self.dic

    def h(self, *args, **kwargs):
        m = hashlib.sha256()
        m.update(json.dumps(args, sort_keys=True).encode("utf-8"))
        m.update(json.dumps(kwargs, sort_keys=True).encode("utf-8"))
        m.update(json.dumps(self.dic, sort_keys=True).encode("utf-8"))
        return m.hexdigest()

    def keys(self):
        return self.dic.keys()


class Selection:
    def __init__(self, *args, **kwargs):
        self.kwargs = {}
        for a in args:
            if isinstance(a, dict):
                self.kwargs.update(a)
                continue
            assert False, a

        self.kwargs.update(kwargs)

        print("--", self.kwargs)

        class InList:
            def __init__(self, lst):
                self.lst = lst

            def __call__(self, x):
                return x in self.lst

        self.actions = {}
        for k, v in self.kwargs.items():
            if v is None:
                self.actions[k] = lambda x: True
                return

            if not isinstance(v, (list, tuple, set)):
                v = [v]

            v = set(v)

            self.actions[k] = InList(v)

    def match_element(self, element):
        return all(v(element.metadata(k)) for k, v in self.actions.items())

    @property
    def is_empty(self):
        return not self.kwargs


class Order:
    def __init__(self, *args, **kwargs):
        self.kwargs = {}
        for a in args:
            if isinstance(a, dict):
                self.kwargs.update(a)
                continue
            if isinstance(a, str):
                self.kwargs[a] = "ascending"
                continue
            assert False, a

        self.kwargs.update(kwargs)

        self.actions = self.build_actions(self.kwargs)

    def compare_elements(self, a, b):
        for k, v in self.actions.items():
            n = v(a.metadata(k), b.metadata(k))
            if n != 0:
                return n
        return 0

    @property
    def is_empty(self):
        return not self.kwargs


class SimpleOrder(Order):
    def build_actions(self, kwargs):
        actions = {}

        def ascending(a, b):
            if a == b:
                return 0
            if a > b:
                return 1
            if a < b:
                return -1
            raise ValueError(f"{a},{b}")

        def descending(a, b):
            if a == b:
                return 0
            if a > b:
                return -1
            if a < b:
                return 1
            raise ValueError(f"{a},{b}")

        class Compare:
            def __init__(self, order):
                self.order = order

            def __call__(self, a, b):
                return ascending(self.order[a], self.order[b])

        for k, v in kwargs.items():
            if v == "ascending" or v is None:
                actions[k] = ascending
                continue

            if v == "descending":
                actions[k] = descending
                continue

            assert isinstance(
                v, (list, tuple)
            ), f"Invalid argument for {k}: {v} ({type(v)})"

            order = {key: i for i, key in enumerate(v)}
            actions[k] = Compare(order)

        return actions


class Index(Source):
    @classmethod
    def new_mask_index(self, *args, **kwargs):
        return MaskIndex(*args, **kwargs)

    def __init__(self, *args, order_by=None, **kwargs):
        self._init_args = args
        self._init_kwargs = kwargs
        self._init_order_by = order_by
        self._coords = {}

    def mutate(self):
        source = self
        source = source.sel(*self._init_args, **self._init_kwargs)
        source = source.order_by(*self._init_args, **self._init_kwargs)
        if self._init_order_by is not None:
            source = source.order_by(self._init_order_by)
        return source

    @abstractmethod
    def __getitem__(self, n):
        self._not_implemented()

    @abstractmethod
    def __len__(self):
        self._not_implemented()

    @abstractmethod
    def sel(self, *args, **kwargs):
        """Filter elements on their metadata(), according to kwargs.
        Returns a new index object.
        """
        selection = Selection(*args, **kwargs)
        if selection.is_empty:
            return self

        indices = (
            i for i, element in enumerate(self) if selection.match_element(element)
        )

        return self.new_mask_index(self, indices)

    def order_by(self, *args, **kwargs):
        """Default order_by method.
        It expects that calling self[i] returns an element that and Order object can rank
        (i.e. order.get_element_ranking(element) -> tuple).
        then it sorts the elements according to the tuples.

        Returns a new index object.
        """

        order = SimpleOrder(*args, **kwargs)
        if order.is_empty:
            return self

        def cmp(i, j):
            return order.compare_elements(self[i], self[j])

        indices = list(range(len(self)))
        indices = sorted(indices, key=functools.cmp_to_key(cmp))
        return self.new_mask_index(self, indices)

    def from_slice(self, s):
        indices = range(len(self))[s]
        return self.new_mask_index(self, indices)

    def to_numpy(self, *args, **kwargs):
        import numpy as np

        return np.array([f.to_numpy(*args, **kwargs) for f in self])

    def to_pytorch_tensor(self, *args, **kwargs):
        import torch

        return torch.Tensor(self.to_numpy(*args, **kwargs))


class MaskIndex(Index):
    def __init__(self, index, indices):
        self.index = index
        self.indices = list(indices)
        super().__init__(
            *self.index._init_args,
            order_by=self.index._init_order_by,
            **self.index._init_kwargs,
        )

    def __getitem__(self, n):
        if isinstance(n, slice):
            return self.from_slice(n)

        n = self.indices[n]
        return self.index[n]

    def __len__(self):
        return len(self.indices)

    def __repr__(self):
        return "MaskIndex(%r,%s)" % (self.index, self.indices)


class MultiIndex(Index):
    def __init__(self, indexes, *args, **kwargs):
        self.indexes = list(indexes)
        super().__init__(*args, **kwargs)
        # self.indexes = list(i for i in indexes if len(i))
        # TODO: propagate  index._init_args, index._init_order_by, index._init_kwargs, for each i in indexes?

    def sel(self, *args, **kwargs):
        selection = Selection(*args, **kwargs)
        if selection.is_empty:
            return self
        return self.__class__(i.sel(*args, **kwargs) for i in self.indexes)

    def __getitem__(self, n):
        if isinstance(n, slice):
            return self.from_slice(n)

        k = 0
        while n >= len(self.indexes[k]):
            n -= len(self.indexes[k])
            k += 1
        return self.indexes[k][n]

    def __len__(self):
        return sum(len(i) for i in self.indexes)

    def graph(self, depth=0):
        print(" " * depth, self.__class__.__name__)
        for s in self.indexes:
            s.graph(depth + 3)

    def __repr__(self):
        return "MultiFieldSet(%s)" % ",".join(repr(i) for i in self.indexes)


class ForwardingIndex(Index):
    def __init__(self, index):
        self.index = index

    def __len__(self):
        return len(self.index)


class ScaledField:
    def __init__(self, field, offset, scaling):
        self.field = field
        self.offset = offset
        self.scaling = scaling

    def to_numpy(self, **kwargs):
        return (self.field.to_numpy(**kwargs) - self.offset) * self.scaling


class ScaledIndex(ForwardingIndex):
    def __init__(self, index, offset, scaling):
        super().__init__(index)
        self.offset = offset
        self.scaling = scaling

    def __getitem__(self, n):
        if isinstance(n, slice):
            return self.from_slice(n)
        return ScaledField(self.index[n], self.offset, self.scaling)
