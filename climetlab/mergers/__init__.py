# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from climetlab.sources.file import FileSource

LOG = logging.getLogger(__name__)


def _nearest_common_class(objects):

    # mro() is "method resolution order"
    mros = [type(o).mro() for o in objects]

    first = mros[0]
    rest = mros[1:]
    for c in first:
        if all(c in m for m in rest):
            return c

    assert False


def _flatten(sources):
    from climetlab.sources.multi import MultiSource

    for s in sources:
        if isinstance(s, MultiSource) and s.merger is None:
            yield from _flatten(s.sources)
        else:
            yield s


class Merger:
    def __init__(self, sources):

        assert sources

        self.sources = list(_flatten(sources))
        assert self.sources, sources

        self.paths = None
        self.reader_class = None
        self.common = _nearest_common_class(sources)
        LOG.debug("nearest_common_class %s", self.common)

        if issubclass(self.common, FileSource):
            readers = [s._reader for s in self.sources]
            self.reader_class = _nearest_common_class(readers)
            LOG.debug("nearest_common_class %s", self.reader_class)
            self.paths = [s.path for s in self.sources]


class DefaultMerger(Merger):
    def to_pandas(self, **kwargs):
        from .pandas import merge

        return merge(
            sources=self.sources,
            paths=self.paths,
            reader_class=self.reader_class,
            **kwargs,
        )

    def to_tfdataset(self, **kwargs):
        from .tfdataset import merge

        return merge(
            sources=self.sources,
            paths=self.paths,
            reader_class=self.reader_class,
            **kwargs,
        )

    def to_xarray(self, **kwargs):
        from .xarray import merge

        return merge(
            sources=self.sources,
            paths=self.paths,
            reader_class=self.reader_class,
            **kwargs,
        )


class ChainedMerger(Merger):
    pass


class CallableMerger(Merger):
    def __init__(self, merger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.merger = merger

    def to_xarray(self, **kwargs):
        if self.paths:
            return self.merger(self.paths, **kwargs)
        return self.merger(self.sources, **kwargs)


def make_merger(merger, sources):
    if callable(merger):
        return CallableMerger(merger, sources)

    if isinstance(merger, (list, tuple)):
        return ChainedMerger(merger, [make_merger(m, sources) for m in merger])

    assert merger is None, "For now..."
    return DefaultMerger(sources)
