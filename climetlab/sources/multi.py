# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import itertools
from . import DataSource


class MultiSource(DataSource):
    def __init__(self, *sources):
        if len(sources) == 1 and isinstance(sources[0], list):
            sources = sources[0]

        self.sources = sources
        self._lengths = [None] * len(sources)

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

    def __len__(self):
        return sum(self._length(i) for i, _ in enumerate(self.sources))

    def _length(self, i):
        if self._lengths[i] is None:
            self._lengths[i] = len(self.sources[i])
        return self._lengths[i]

    def to_xarray(self):
        import xarray as xr

        # return xr.concat(s.to_xarray() for s in self.sources)
        return xr.merge(s.to_xarray() for s in self.sources)


source = MultiSource
