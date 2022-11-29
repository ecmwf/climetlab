# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import hashlib
import json
import logging
from abc import abstractmethod

from climetlab.decorators import alias_argument
from climetlab.sources import Source

LOG = logging.getLogger(__name__)


class OrderOrSelection:
    def __init__(self, *args, **kwargs):
        """Parse args and kwargs to build a dictionary in self.order"""
        self.dic = {}

        for arg in args:
            if isinstance(arg, dict):
                arg = self.normalize_naming(**arg)
            res_ok = self.parse_arg(arg)
            if res_ok is False:
                raise ValueError(f"Invalid argument of type({type(arg)}): {arg}")

        kwargs = self.normalize_naming(**kwargs)
        for k, v in kwargs.items():
            self.parse_kwarg(k, v)

    @alias_argument("levelist", ["level"])
    @alias_argument("param", ["variable", "parameter"])
    @alias_argument("number", ["realization", "realisation"])
    @alias_argument("class", "klass")
    def normalize_naming(self, **kwargs):
        return kwargs

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
    def is_empty(self):  # TODO: use __bool__ instead
        if not self.dic:
            return True
        return False

    def h(self, *args, **kwargs):
        m = hashlib.sha256()
        m.update(json.dumps(args, sort_keys=True).encode("utf-8"))
        m.update(json.dumps(kwargs, sort_keys=True).encode("utf-8"))
        m.update(json.dumps(self.dic, sort_keys=True).encode("utf-8"))
        return m.hexdigest()

    def keys(self):
        return self.dic.keys()


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
            if v is None:
                continue
            value = element.metadata(k)
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

    def filter_values(self, key, values):
        if key not in self.dic:
            return values
        vals = self.dic[key]
        return [v for v in vals if v in values]


class Order(OrderOrSelection):
    def __init__(self, *args, **kwargs):
        self._rankers = None
        if args and all([isinstance(a, str) for a in args]):
            args = [args]
        super().__init__(*args, **kwargs)

    @property
    def order(self):
        return self.dic

    def update(self, other):
        assert isinstance(other, Order), other
        self.dic.update(other.dic)

    def items(self):
        if self.is_empty:
            return

        from climetlab.indexing.database.sql import GRIB_INDEX_KEYS

        for k, v in self.dic.items():
            yield k, v

        for k in GRIB_INDEX_KEYS:
            if k in self.dic:
                continue  # already yielded above
            yield k, self[k]

    def __getitem__(self, key):
        # Default is ascending order
        return self.dic.get(key, "ascending")

    def parse_arg(self, arg):
        if super().parse_arg(arg):
            return True
        if isinstance(arg, str):
            self.dic[arg] = "ascending"
            return True
        if isinstance(arg, (list, tuple)):
            dic = {}
            for k in arg:
                assert isinstance(k, str), k
                assert len(k) > 0, k
                if k[0] == "-":
                    dic[k[1:]] = "descending"
                    continue
                if k[0] == "+":
                    dic[k[1:]] = "ascending"
                    continue
                dic[k] = "ascending"
            dic = self.normalize_naming(**dic)
            return self.parse_arg(dic)
        return False

    def parse_kwarg(self, k, v):
        if isinstance(v, (list, tuple)):
            v = [str(_) for _ in v]  # processing only strings from now.
        if (v == "ascending") or (v == "descending") or isinstance(v, (list, tuple)):
            self.dic[k] = v
            return

        if v is None:
            self.dic[k] = "ascending"
            return

        self.dic[k] = "ascending"
        return
        # raise ValueError(f"Invalid argument for {k}: {v} ({type(v)})")

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
                key_types[key] = "explicit"
                continue

            if lst == "ascending" or lst is None:
                dict_of_dicts[key] = lambda value: value
                key_types[key] = "ascending"
                continue

            raise ValueError(f"Invalid argument {lst}")

        self._rankers = keys, key_types, dict_of_dicts
        return self._rankers

    def get_element_ranking(self, element):
        keys, key_types, dict_of_dicts = self.build_rankers()
        ranks = []
        for k in keys:
            value = element.metadata(k)

            if key_types[k] == "ascending":
                ranks.append(value)
                continue

            if key_types[k] == "explicit":
                value = str(value)
                ranks.append(dict_of_dicts[k][value])
                continue

            assert False, (k, key_types[k], element)

        return tuple(ranks)

    def filter_values(self, key, values):
        # TODO: merge this method with get_element_ranking, refactor with "Sorter" class

        keys, key_types, dict_of_dicts = self.build_rankers()
        if key not in dict_of_dicts:
            return values
        vals = dict_of_dicts[key]
        if isinstance(vals, dict):
            sorter = lambda x: vals[x]  # noqa
        elif callable(vals):
            sorter = vals
        else:
            assert False, vals
        return sorted(values, key=sorter)

        assert False, (key, key_types[key], values)


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

        indices = []
        for i, element in enumerate(self):
            if selection.match_element(element):
                indices.append(i)

        return self.new_mask_index(self, indices)

    def order_by(self, *args, **kwargs):
        """Default order_by method.
        It expects that calling self[i] returns an element that and Order object can rank
        (i.e. order.get_element_ranking(element) -> tuple).
        then it sorts the elements according to the tuples.

        Returns a new index object.
        """

        order = Order(*args, **kwargs)
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
                    _self._cache[i] = _self.order.get_element_ranking(element)
                return _self._cache[i]

        sorter = Sorter(self, order)

        result = list(range(len(self)))
        indices = sorted(result, key=sorter)
        return self.new_mask_index(self, indices)


class MaskIndex(Index):
    def __init__(self, index, indices):
        self.index = index
        self.indices = indices
        super().__init__(
            *self.index._init_args,
            order_by=self.index._init_order_by,
            **self.index._init_kwargs,
        )

    def __getitem__(self, n):
        n = self.indices[n]
        return self.index[n]

    def __len__(self):
        return len(self.indices)


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

    def to_numpy(self):
        return (self.field.to_numpy() - self.offset) * self.scaling


class ScaledIndex(ForwardingIndex):
    def __init__(self, index, offset, scaling):
        super().__init__(index)
        self.offset = offset
        self.scaling = scaling

    def __getitem__(self, n):
        return ScaledField(self.index[n], self.offset, self.scaling)
