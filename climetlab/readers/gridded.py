# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from .multi import MultiReaders


class DefaultMerger:
    def __init__(self, engine, backend_kwargs):
        self.engine = engine
        self.backend_kwargs = backend_kwargs

    def merge(self, paths, **kwargs):
        import xarray as xr

        options = dict(backend_kwargs=self.backend_kwargs)
        options.update(kwargs)
        return xr.open_mfdataset(
            paths,
            engine=self.engine,
            **options,
        )


class GriddedMultiReaders(MultiReaders):
    backend_kwargs = {}

    def to_xarray(self, merger=None, **kwargs):
        if merger is None:
            merger = DefaultMerger(self.engine, self.backend_kwargs)
        return merger.merge([r.path for r in self.readers], **kwargs)
