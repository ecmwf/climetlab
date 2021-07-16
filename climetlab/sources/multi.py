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

from climetlab.sources.empty import EmptySource

from . import Source


def infer_open_mfdataset_kwargs(sources, user_kwargs):
    result = {}
    ds = sources[0].to_xarray()
    # lat_dims = [s.get_lat_dim() for s in sources]

    if ds.dims == ["lat", "lon", "forecast_time"]:
        result["concat_dim"] = "forecast_time"

    result.update(user_kwargs)
    return result


class MultiSource(Source):
    def __init__(self, *sources, filter=None, merger=None):
        if not merger:
            merger = DefaultMerger()

        if len(sources) == 1 and isinstance(sources[0], list):
            sources = sources[0]

        # src = []
        # for s in sources:
        #     s = s.mutate()  # Just in case
        #     if not s.ignore():
        #         src += s.flatten()

        self.sources = [s.mutate() for s in sources]
        self.filter = filter
        self.merger = merger
        self._lengths = [None] * len(self.sources)

    def ignore(self):
        return len(self.sources) == 0

    def flatten(self):
        return self.sources

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

    def to_xarray(self, **kwargs):

        merger = "hindcast"

        merger = "merge(concat(forecast_dim))"

        paths = [s.get_path() for s in self.sources]

        return self.merger.to_xarray_from_path(self.sources, paths, **kwargs)

        import xarray as xr
        from xarray.backends.common import BackendEntrypoint

        class MyEngine(BackendEntrypoint):
            @classmethod
            def open_dataset(cls, filename_or_obj, *args, **kwargs):
                return filename_or_obj.to_xarray()

        options = infer_open_mfdataset_kwargs(self.sources, kwargs)

        if False:  # all self sources is path:
            return xr.open_mfdataset([s.path for s in self.sources], **options)
        else:
            return xr.open_mfdataset(self.sources, engine=MyEngine, **options)

    def to_tfdataset(self, **kwargs):
        sources = self.sources

        merged = sources[0].multi_merge(sources)
        if merged is not None:
            return merged.to_tfdataset(merger=self.merger, **kwargs)

        ds = sources[0].to_tfdataset()
        for s in sources[1:]:
            ds = ds.concatenate(s.to_tfdataset())

        return ds

    def to_pandas(self, **kwargs):
        if self.merger:
            return self.merger.to_pandas(self.sources, **kwargs)

        import pandas

        return pandas.concat([s.to_pandas() for s in self.sources])

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


source = MultiSource
