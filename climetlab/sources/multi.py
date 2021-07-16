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
from collections import defaultdict

from climetlab.sources.empty import EmptySource

from . import Source
from .file import FileSource

LOG = logging.getLogger(__name__)


def nearest_common_class(objects):


    # mro() is "method resolution order"
    mros = [type(o).mro() for o in objects]

    first = mros[0]
    rest = mros[1:]
    for c in first:
        if all(c in m for m in rest):
            return c

    assert False


class Merger:
    def __init__(self, sources):
        self.sources = sources
        self.readers = None
        self.paths = None
        self.common = nearest_common_class(sources)
        LOG.debug("nearest_common_class %s", self.common)

        readers = []
        if issubclass(self.common, FileSource):
            self.readers = [s._reader for s in self.sources]
            common_reader = nearest_common_class(self.readers)
            LOG.debug("nearest_common_class %s", common_reader)

        for s in sources:
            if isinstance(s, MultiSource):
                # TODO check if it has a merger, otherwise
                # flatten() and combine
                pass



class DefaultMerger(Merger):
    def to_pandas(self, **kwargs):
        import pandas

        return pandas.concat([s.to_pandas(**kwargs) for s in self.sources])

    def to_tfdataset(self, **kwargs):
        ds = self.sources[0].to_tfdataset()
        for s in self.sources[1:]:
            ds = ds.concatenate(s.to_tfdataset())
        return ds

    def to_xarray(self, **kwargs):

        import xarray as xr

        arrays = [s.to_xarray() for s in self.sources]

        # Get values of scalar coordinates
        values = defaultdict(set)
        for a in arrays:
            for v in a.coords:
                if len(a[v].shape) == 0:
                    vals = a[v].values
                    # assert len(vals) == 1, (v, vals)
                    values[v].add(float(vals))

        # Promote scalar coordinates
        promote = [name for name, count in values.items() if len(count) > 1]

        if promote:
            dims = dict(zip(promote, [1] * len(promote)))
            arrays = [a.expand_dims(dims) for a in arrays]

        return xr.merge(arrays)


class MultiSource(Source):
    def __init__(self, *sources, filter=None, merger=None):
        if len(sources) == 1 and isinstance(sources[0], list):
            sources = sources[0]

        self.sources = [s.mutate() for s in sources if not s.ignore()]
        self.filter = filter
        self.merger = merger if merger else DefaultMerger
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
        print(" " * depth, self.__class__.__name__)
        for s in self.sources:
            s.graph(depth + 3)

    def to_xarray(self, **kwargs):
        return self.merger(self.sources).to_xarray(**kwargs)

    def to_tfdataset(self, **kwargs):
        return self.merger(self.sources).to_tfdataset(**kwargs)

    def to_pandas(self, **kwargs):
        return self.merger(self.sources).to_pandas(**kwargs)


source = MultiSource
