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
from climetlab.utils import string_to_args

LOG = logging.getLogger(__name__)

FORWARDS = ("to_xarray", "to_pandas", "to_tfdataset")


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


def merge_by_class(sources):
    common = _nearest_common_class(sources)
    return common.merge(sources)


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

    @property
    def paths_or_sources(self):
        if self.paths is not None:
            return self.paths
        return self.sources


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


class ObjMerger(Merger):
    def __init__(self, obj, sources, *args, **kwargs):
        super().__init__(sources)
        self.obj = obj

    def to_xarray(self, *args, **kwargs):
        return self.obj.to_xarray(self.paths_or_sources, **kwargs)

    def to_pandas(self, *args, **kwargs):
        return self.obj.to_pandas(self.paths_or_sources, **kwargs)

    def to_tfdataset(self, *args, **kwargs):
        return self.obj.to_tfdataset(self.paths_or_sources, **kwargs)


class CallableMerger(Merger):
    def __init__(self, func, sources, *args, **kwargs):
        super().__init__(sources)
        self.func = func

    def _call_func(self, *args, **kwargs):
        return self.func(self.paths_or_sources, **kwargs)

    to_xarray = _call_func
    to_pandas = _call_func
    to_tfdataset = _call_func


class XarrayGenericMerger(Merger):
    def __init__(self, sources, **options):
        super().__init__(sources)
        self.options = options

    def to_xarray(self, *args, **kwargs):
        assert self.paths is not None, self.paths
        import xarray as xr

        options = {}
        options.update(self.default_options)
        options.update(self.options)
        options.update(kwargs)
        LOG.debug(f"xr.open_mfdataset with options = {options}")
        return xr.open_mfdataset(
            self.paths,
            **options,
        )


class XarrayConcatMerger(XarrayGenericMerger):
    def __init__(self, sources, **options):
        if "dim" in options:
            dim = options.pop("dim")
            options["concat_dim"] = dim
        super().__init__(sources, **options)

    default_options = {"combine": "nested"}


class XarrayMerger(XarrayGenericMerger):
    default_options = {}


MERGERS = {
    "concat": XarrayConcatMerger,
    "merge": DefaultMerger,
}


def add_default_values_and_kwargs(args):
    kwargs = dict()
    for a in args:
        k, v = a.split("=")
        kwargs[k] = v
    return kwargs


def make_merger(merger, sources):

    for fwd in FORWARDS:
        if hasattr(merger, fwd) and callable(getattr(merger, fwd)):
            LOG.debug("Merger %s has method in %s()", merger, fwd)
            return ObjMerger(merger, sources)

    if callable(merger):
        LOG.debug("Merger %s is callable", merger)
        return CallableMerger(merger, sources)

    if isinstance(merger, str):
        name, args, kwargs = string_to_args(merger)
        return MERGERS[name](sources, *args, **kwargs)

    if isinstance(merger, tuple):
        if len(merger) == 2 and isinstance(merger[1], dict):
            return MERGERS[merger[0]](sources, **merger[1])
        return MERGERS[merger[0]](sources, *merger[1:])

    if merger is None:
        LOG.debug("Using DefaultMerger")
        return DefaultMerger(sources)

    raise ValueError(f"Unsupported merger {merger} ({type(merger)})")
