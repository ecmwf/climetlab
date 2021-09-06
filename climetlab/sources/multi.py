# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import itertools
import logging

from climetlab.mergers import make_merger
from climetlab.sources.empty import EmptySource

from . import Source

LOG = logging.getLogger(__name__)


class MultiSource(Source):
    def __init__(self, *sources, filter=None, merger=None):

        if len(sources) == 1 and isinstance(sources[0], list):
            sources = sources[0]

        self.sources = [s.mutate() for s in sources if not s.ignore()]
        self.filter = filter
        self.merger = merger
        self._lengths = [None] * len(self.sources)

    def ignore(self):
        return len(self.sources) == 0

    def mutate(self):

        if len(self.sources) == 1 and self.merger is None:
            return self.sources[0].mutate()

        if len(self.sources) == 0:
            return EmptySource()

        return self

    def _set_dataset(self, dataset):
        super()._set_dataset(dataset)
        for s in self.sources:
            s._set_dataset(dataset)

    def __iter__(self):
        return itertools.chain(*self.sources)

    def __getitem__(self, n):

        if n < 0:
            n = len(self) + n

        i = 0
        while n >= self._length(i):
            n -= self._length(i)
            i += 1
        return self.sources[i][n]

    def sel(self, *args, **kwargs):
        raise NotImplementedError

    def __len__(self):
        return sum(self._length(i) for i, _ in enumerate(self.sources))

    def _length(self, i):
        if self._lengths[i] is None:
            self._lengths[i] = len(self.sources[i])
        return self._lengths[i]

    def __repr__(self) -> str:
        string = ",".join(repr(s) for s in self.sources)
        return f"{self.__class__.__name__}({string})"

    def save(self, path):
        with open(path, "wb") as f:
            for s in self.sources:
                s.write(f)

    def graph(self, depth=0):
        print(" " * depth, self.__class__.__name__, self.merger)
        for s in self.sources:
            s.graph(depth + 3)

    def to_xarray(self, **kwargs):
        return make_merger(self.merger, self.sources).to_xarray(**kwargs)

    def to_tfdataset(self, **kwargs):
        return make_merger(self.merger, self.sources).to_tfdataset(**kwargs)

    def to_pandas(self, **kwargs):
        return make_merger(self.merger, self.sources).to_pandas(**kwargs)


source = MultiSource
