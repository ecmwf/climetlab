# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging
import warnings
from abc import abstractmethod

from climetlab.sources import Source

LOG = logging.getLogger(__name__)


class OrderOrSelection:
    def __init__(self, *args, **kwargs):
        """Parse args and kwargs to build a dictionary in self.order"""
        self.dic = {}

        if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            kwargs = args[0]

        for arg in args:
            if not self.parse_arg(arg):
                raise ValueError(f"Invalid argument of type({type(arg)}): {arg}")

        for k, v in kwargs.items():
            self.parse_kwarg(k, v)

        from climetlab.vocabularies.grib import grib_naming

        self.dic = grib_naming(self.dic)

    def parse_arg(self, arg):
        # Returns True of argument has been parsed.
        if arg is None:
            return True
        if isinstance(arg, dict):
            for k, v in arg.items():
                self.parse_kwarg(k, v)
            return True
        return False

    def __str__(self):
        return f"{self.__class__.__name__}({self.dic})"

    @property
    def is_empty(self):
        if not self.dic:
            return True
        return False


# TODO: this should/could be done with decorators
class Selection(OrderOrSelection):
    @property
    def selection(self):
        return self.dic

    def parse_kwarg(self, k, v):
        if v is not None and not isinstance(v, (list, tuple)):
            v = [v]
        if isinstance(v, (list, tuple)):
            v = [str(_) for _ in v]
        self.dic[k] = v
        return

    def match_element(self, element):
        for k, v in self.dic.items():
            key = {
                "param": "short_name",
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
                return False
            if value == v:
                continue
            if str(value) == v:
                continue
            return False
        return True


class Order(OrderOrSelection):
    def __init__(self, *args, **kwargs):
        self._rankers = None
        super().__init__(*args, **kwargs)

    @property
    def order(self):
        return self.dic

    def parse_arg(self, arg):
        if super().parse_arg(arg):
            return True
        if isinstance(arg, str):
            self.dic[arg] = "ascending"
            return True
        return False

    def parse_kwarg(self, k, v):
        if isinstance(v, (list, tuple)):
            v = [str(_) for _ in v]  # processing only strings from now.
        if (
            (v == "ascending")
            or (v == "descending")
            or (v is None)
            or isinstance(v, (list, tuple))
        ):
            self.dic[k] = v
            return
        raise ValueError(f"Invalid argument of type({type(v)}): {k}={v}")

    def build_rankers(self):
        if self._rankers is not None:
            return self._rankers

        from climetlab.indexing.database.sql import GRIB_INDEX_KEYS

        keys = [_ for _ in self.dic.keys()]
        keys += [_ for _ in GRIB_INDEX_KEYS if _ not in keys]

        key_types = {}
        dict_of_dicts = dict()

        for key in keys:
            lst = self.dic.get(key, None)

            if isinstance(lst, (tuple, list)):
                dict_of_dicts[key] = dict(zip(lst, range(len(lst))))
                key_types[key] = None
                continue

            if lst == "ascending" or lst is None:
                dict_of_dicts[key] = lambda value: value
                key_types[key] = "ascending"
                continue

            raise ValueError(f"Invalid argument {lst}")

        self._rankers = keys, key_types, dict_of_dicts
        return self._rankers

    def rank(self, element):
        keys, key_types, dict_of_dicts = self.build_rankers()
        ranks = []
        for k in keys:
            if k == "param":
                # TODO: clean this
                value = element.metadata("short_name")
            else:
                try:
                    value = element.metadata(k)
                except KeyError:
                    warnings.warn(f"Cannot find all metadata keys.")

            if key_types[k] == "ascending":
                ranks.append(value)
                continue

            assert key_types[k] is None, (k, key_types[k], element)
            value = str(value)
            ranks.append(dict_of_dicts[k][value])

        return tuple(ranks)


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

        indices = []
        for i, element in enumerate(self):
            if selection.match_element(element):
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
            assert isinstance(v, (tuple, list)) or v in [
                "ascending",
                None,
            ], f"Unsupported order: {v}, Supported values: 'ascending'."

        class Sorter:
            def __init__(_self, index, order):
                """Uses the order to sort the index"""

                _self.index = index
                _self.order = order
                _self._cache = [None] * len(_self.index)

            def __call__(_self, i):
                if _self._cache[i] is None:
                    element = _self.index[i]
                    _self._cache[i] = _self.order.rank(element)
                return _self._cache[i]

        sorter = Sorter(self, order)

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
