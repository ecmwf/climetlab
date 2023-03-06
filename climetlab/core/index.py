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


@alias_argument("levelist", ["level"])
@alias_argument("param", ["variable", "parameter"])
@alias_argument("number", ["realization", "realisation"])
@alias_argument("class", "klass")
def normalize_naming(self, **kwargs):
    return kwargs

class OrderOrSelection:
    def __str__(self):
        return f"{self.__class__.__name__}({self.dic})"

    @property
    def is_empty(self):
        return not self.kwargs

    def h(self):
        m = hashlib.sha256()
        m.update(str(self.__class__.__name__)).encode("utf-8")
        m.update(json.dumps(self.kwargs, sort_keys=True).encode("utf-8"))
        return m.hexdigest()


class Selection(OrderOrSelection):
    def __init__(self, *args, **kwargs):
        self.kwargs = {}
        for a in args:
            if isinstance(a, dict):
                self.kwargs.update(a)
                continue
            assert False, a

        self.kwargs.update(kwargs)

        self.actions = self.build_actions(self.kwargs)

    def build_actions(self, kwargs):
        class InList:
            def __init__(self, lst):
                self.lst = lst

            def __call__(self, x):
                return x in self.lst

        actions = {}
        for k, v in self.kwargs.items():
            if v is None:
                actions[k] = lambda x: True
                continue

            if callable(v):
                actions[k] = v
                continue

            if not isinstance(v, (list, tuple, set)):
                v = [v]

            v = set(v)

            actions[k] = InList(v)

        return actions

    def match_element(self, element):
        return all(v(element.metadata(k)) for k, v in self.actions.items())


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

            if callable(v):
                actions[k] = v
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

    def __getitem__(self, n):
        if isinstance(n, slice):
            return self.from_slice(n)
        if isinstance(n, (list, tuple)):
            return self.from_list(n)
        if isinstance(n, dict):
            return self.from_dict(n)
        return self._getitem(n)

    def from_slice(self, s):
        indices = range(len(self))[s]
        return self.new_mask_index(self, indices)

    def from_list(self, lst):
        indices = [i for i, x in enumerate(lst) if x]
        return self.new_mask_index(self, indices)

    def from_dict(self, dic):
        return self.sel(dic)

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

    def _getitem(self, n):
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

    def _getitem(self, n):
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
