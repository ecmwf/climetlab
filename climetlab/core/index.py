# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging
from abc import abstractmethod

from climetlab.sources import Source

LOG = logging.getLogger(__name__)

# TODO: this should/could be done with decorators
class Selection:
    def __init__(self, *args, **kwargs):
        """Parse args and kwargs to build a dictionary in self.selection"""

        if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            kwargs = args[0]

        self.selection = kwargs

    @property
    def is_empty(self):
        if not self.selection:
            return True
        return False


class Order:
    def __init__(self, *args, **kwargs):
        """Parse args and kwargs to build a dictionary in self.order"""
        self.order = {}

        if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            kwargs = args[0]

        for arg in args:
            self.parse_arg(arg)

        for k, v in kwargs.items():
            self.parse_kwarg(k, v)

    def __str__(self):
        return f"{self.__class__.__name__}({self.order})"

    @property
    def is_empty(self):
        if not self.order:
            return True
        return False

    def parse_arg(self, arg):
        if arg is None:
            return
        if isinstance(arg, dict):
            for k, v in arg.items():
                self.parse_kwarg(k, v)
            return
        if isinstance(arg, str):
            self.order[arg] = "ascending"
            return
        raise ValueError(f"Invalid argument of type({type(arg)}): {arg}")

    def parse_kwarg(self, k, v):
        if (
            (v == "ascending")
            or (v == "descending")
            or (v is None)
            or isinstance(v, (list, tuple))
        ):
            self.order[k] = v
            return
        raise ValueError(v)


class Index(Source):

    ORDER_CLASS = Order
    SELECTION_CLASS = Selection

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
        selection = self.SELECTION_CLASS(*args, **kwargs)

        from climetlab.vocabularies.grib import grib_naming

        selection.selection = grib_naming(selection.selection)

        def match(element, selection):
            for k, v in selection.items():
                key = {
                    "param": "shortName",
                }.get(k, k)
                if v is None:
                    continue
                value = element.metadata(key)
                # value = grib_naming({key:value})[key]
                if isinstance(v, (list, tuple)):
                    if value in v:
                        continue
                    if str(value) in v:
                        continue
                    print(f"{element}: {k}/{key}={value} not in {v}")
                    return False
                if value == v:
                    continue
                if str(value) == v:
                    continue
                print(f"{element}: {k}/{key}={value} != {v}")
                return False
            return True

        indices = []
        for i, element in enumerate(self):
            if match(element, selection.selection):
                indices.append(i)

        return MaskIndex(self, indices)

    def order_by(self, *args, **kwargs):
        """Default order_by method.
        It expects that calling self[i] returns an element with a .metadata(key) method,
        then sort the tuple.
        Returns a new index object.
        """

        order = self.ORDER_CLASS(*args, **kwargs)
        if order.is_empty:
            return self

        for k, v in order.order.items():
            assert isinstance(v, (list, tuple)) or v in [
                "ascending",
                None,
            ], f"Unsupported order: {v}."

        class Sorter:
            def __init__(_self, index, order):
                """Uses the order to sort the index"""

                _self.index = index
                _self.order = order
                _self._cache = [None] * len(_self.index)

            def __call__(_self, i):
                if _self._cache[i] is None:
                    element = _self.index[i]
                    _self._cache[i] = tuple(
                        element.metadata(k) for k in _self.order.keys()
                    )
                return _self._cache[i]

        sorter = Sorter(self, order.order)

        result = list(range(len(self)))
        indices = sorted(result, key=sorter)
        return MaskIndex(self, indices)


class MaskIndex(Index):
    def __init__(self, index, indices):
        self.index = index
        self.indices = indices

    def __getitem__(self, n):
        n = self.indices[n]
        return self.index[n]

    def __len__(self):
        return len(self.indices)


class MultiIndex(Index):
    def __init__(self, indexes):
        self.indexes = list(indexes)
        # self.indexes = list(i for i in indexes if len(i))

    def sel(self, *args, **kwargs):
        return self.__class__(i.sel(*args, **kwargs) for i in self.indexes)

    def __getitem__(self, n):
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


class ForewardingIndex(Index):
    def __init__(self, index):
        self.index = index

    def __len__(self):
        return len(self.index)


class ScaledField:
    def __init__(self, field, offset, scaling):
        self.field = field
        self.offset = offset
        self.scaling = scaling

    def to_numpy(self):
        return (self.field.to_numpy() - self.offset) * self.scaling


class ScaledIndex(ForewardingIndex):
    def __init__(self, index, offset, scaling):
        super().__init__(index)
        self.offset = offset
        self.scaling = scaling

    def __getitem__(self, n):
        return ScaledField(self.index[n], self.offset, self.scaling)
