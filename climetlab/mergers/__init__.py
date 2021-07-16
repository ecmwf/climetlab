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


class Merger:
    def __init__(self, sources):
        self.sources = sources
        self.readers = None
        self.paths = None
        self.common = _nearest_common_class(sources)
        LOG.debug("nearest_common_class %s", self.common)

        readers = []
        if issubclass(self.common, FileSource):
            self.readers = [s._reader for s in self.sources]
            common_reader = _nearest_common_class(self.readers)
            LOG.debug("nearest_common_class %s", common_reader)

        # for s in sources:
        #     if isinstance(s, MultiSource):
        #         # TODO check if it has a merger, otherwise
        #         # flatten() and combine
        #         pass


class DefaultMerger(Merger):
    def to_pandas(self, **kwargs):
        from .pandas import merge

        return merge(
            source=self.sources,
            paths=self.paths,
            readers=self.readers,
            **kwargs,
        )

    def to_tfdataset(self, **kwargs):
        from .tfdataset import merge

        return merge(
            source=self.sources,
            paths=self.paths,
            readers=self.readers,
            **kwargs,
        )

    def to_xarray(self, **kwargs):
        from .xarray import merge

        return merge(
            source=self.sources,
            paths=self.paths,
            readers=self.readers,
            **kwargs,
        )


def make_merger(merger, sources):
    assert merger is None, "For now..."
    return DefaultMerger(sources)
