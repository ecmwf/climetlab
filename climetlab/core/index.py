# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import functools
import logging
import math
from abc import abstractmethod
from collections import defaultdict

import climetlab as cml
from climetlab.core.order import normalize_order_by
from climetlab.core.select import normalize_selection
from climetlab.loaders import build_remapping
from climetlab.sources import Source

LOG = logging.getLogger(__name__)


class OrderOrSelection:
    def __str__(self):
        return f"{self.__class__.__name__}({self.kwargs})"

    @property
    def is_empty(self):
        return not self.kwargs


class Selection(OrderOrSelection):
    def __init__(self, kwargs, remapping=None):
        self.remapping = build_remapping(remapping)

        class InList:
            def __init__(self, lst):
                self.first = True
                self.lst = lst  # lazy casting: lst will be modified

            def __call__(self, x):
                if self.first and x is not None:
                    cast = type(x)
                    self.lst = [cast(y) for y in self.lst]
                    self.first = False
                return x in self.lst

        self.actions = {}
        for k, v in kwargs.items():
            if v is None or v is cml.ALL:
                self.actions[k] = lambda x: True
                continue

            if callable(v):
                self.actions[k] = v
                continue

            if not isinstance(v, (list, tuple, set)):
                v = [v]

            v = set(v)

            self.actions[k] = InList(v)

    def match_element(self, element):
        metadata = self.remapping(element.metadata)
        return all(v(metadata(k)) for k, v in self.actions.items())


class OrderBase(OrderOrSelection):
    def __init__(self, kwargs, remapping):
        self.actions = self.build_actions(kwargs)
        self.remapping = remapping

    @abstractmethod
    def build_actions(self, kwargs):
        raise NotImplementedError()

    def compare_elements(self, a, b):
        assert callable(self.remapping), (type(self.remapping), self.remapping)
        a_metadata = self.remapping(a.metadata)
        b_metadata = self.remapping(b.metadata)
        for k, v in self.actions.items():
            n = v(a_metadata(k), b_metadata(k))
            if n != 0:
                return n
        return 0


class Order(OrderBase):
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
                return ascending(self.get(a), self.get(b))

            def get(self, x):
                return self.order[x]

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

            order = {}
            for i, key in enumerate(v):
                order[str(key)] = i
                try:
                    order[int(key)] = i
                except ValueError:
                    pass
                try:
                    order[float(key)] = i
                except ValueError:
                    pass
            actions[k] = Compare(order)

        return actions


class Index(Source):
    @classmethod
    def new_mask_index(self, *args, **kwargs):
        return MaskIndex(*args, **kwargs)

    @abstractmethod
    def __len__(self):
        self._not_implemented()

    def _normalize_kwargs_names(**kwargs):
        return kwargs

    def sel(self, *args, remapping=None, **kwargs):
        """Filter elements on their metadata(), according to kwargs.
        Returns a new index object.
        """

        kwargs = normalize_selection(*args, **kwargs)
        kwargs = self._normalize_kwargs_names(**kwargs)
        if not kwargs:
            return self

        selection = Selection(kwargs, remapping=remapping)

        indices = (
            i for i, element in enumerate(self) if selection.match_element(element)
        )

        return self.new_mask_index(self, indices)

    def order_by(self, *args, remapping=None, **kwargs):
        """Default order_by method.
        It expects that calling self[i] returns an element that and Order object can rank
        (i.e. order.get_element_ranking(element) -> tuple).
        then it sorts the elements according to the tuples.

        Returns a new index object.
        """
        kwargs = normalize_order_by(*args, **kwargs)
        kwargs = self._normalize_kwargs_names(**kwargs)

        remapping = build_remapping(remapping)

        if not kwargs:
            return self

        order = Order(kwargs, remapping=remapping)

        def cmp(i, j):
            return order.compare_elements(self[i], self[j])

        indices = list(range(len(self)))
        indices = sorted(indices, key=functools.cmp_to_key(cmp))
        return self.new_mask_index(self, indices)

    def __getitem__(self, n):
        if isinstance(n, slice):
            return self.from_slice(n)
        if isinstance(n, tuple):
            return self.from_tuple(n)
        if isinstance(n, list):
            return self.from_mask(n)
        if isinstance(n, dict):
            return self.from_dict(n)
        return self._getitem(n)

    def from_slice(self, s):
        indices = range(len(self))[s]
        return self.new_mask_index(self, indices)

    def from_mask(self, lst):
        indices = [i for i, x in enumerate(lst) if x]
        return self.new_mask_index(self, indices)

    def from_tuple(self, lst):
        return self.new_mask_index(self, lst)

    def from_dict(self, dic):
        return self.sel(dic)

    @classmethod
    def merge(cls, sources):
        assert all(isinstance(_, Index) for _ in sources)
        return MultiIndex(sources)

    def to_numpy(self, *args, **kwargs):
        import numpy as np

        return np.array([f.to_numpy(*args, **kwargs) for f in self])

    def to_pytorch_tensor(self, *args, **kwargs):
        import torch

        return torch.Tensor(self.to_numpy(*args, **kwargs))

    def full(self, *coords):
        return FullIndex(self, *coords)


class MaskIndex(Index):
    def __init__(self, index, indices):
        self.index = index
        self.indices = list(indices)

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
        if not args and not kwargs:
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
        return "%s(%s)" % (
            self.__class__.__name__,
            ",".join(repr(i) for i in self.indexes),
        )


class FullIndex(Index):
    def __init__(self, index, *coords):
        import numpy as np

        self.index = index

        # Pass1, unique values
        unique = index.unique_values(*coords)
        shape = tuple(len(v) for v in unique.values())

        name_to_index = defaultdict(dict)

        for k, v in unique.items():
            for i, e in enumerate(v):
                name_to_index[k][e] = i

        self.size = math.prod(shape)
        self.shape = shape
        self.holes = np.full(shape, False)

        for f in index:
            idx = tuple(name_to_index[k][f.metadata(k)] for k in coords)
            self.holes[idx] = True

        self.holes = self.holes.flatten()
        print("+++++++++", self.holes.shape, coords, self.shape)

    def __len__(self):
        return self.size

    def _getitem(self, n):
        assert self.holes[n], f"Attempting to access hole {n}"
        return self.index[sum(self.holes[:n])]
