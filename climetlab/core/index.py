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


class Index(Source):
    @abstractmethod
    def __getitem__(self, n):
        self._not_implemented()

    @abstractmethod
    def __len__(self):
        self._not_implemented()

    @abstractmethod
    def sel(self, kwargs):
        self._not_implemented()


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
