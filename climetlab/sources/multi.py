# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import itertools
from collections import defaultdict

from . import Source


class MultiSource(Source):
    def __init__(self, *sources, merger=None):
        if len(sources) == 1 and isinstance(sources[0], list):
            sources = sources[0]
        self.merger = merger
        self.sources = sources
        self._lengths = [None] * len(sources)

    def mutate(self):
        if len(self.sources) == 1 and self.merger is None:
            return self.sources[0].mutate()
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

    def to_xarray(self, **kwargs):
        import xarray as xr

        merged = self.sources[0].multi_merge(self.sources)
        if merged is not None:
            return merged.to_xarray(merger=self.merger, **kwargs)

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


source = MultiSource
