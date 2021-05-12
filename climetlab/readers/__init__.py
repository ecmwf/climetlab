# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import warnings
import weakref
from importlib import import_module

from climetlab.decorators import locked


class Reader:
    def __init__(self, source, path):
        self._source = weakref.ref(source)
        self.path = path

    @property
    def source(self):
        return self._source()

    def mutate(self):
        # Give a chance to `directory` or `zip` to change the reader
        return self

    def sel(self, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def multi_merge(cls, readers):
        return None


class MultiReaders:
    backend_kwargs = {}

    def __init__(self, readers):
        self.readers = readers

    def to_xarray(self, **kwargs):
        import xarray as xr

        readers = {r.path: r for r in self.readers}

        def preprocess(ds):
            r = readers[ds.encoding["source"]]
            return r.source.post_xarray_open_dataset_hook(ds)

        options = None
        for r in self.readers:
            opts = r.source.cfgrib_options()
            if options is None:
                options = opts
            else:
                assert options == opts, f"{options} != {opts}"

        options.update(kwargs)
        options.setdefault("backend_kwargs", {})
        options["backend_kwargs"].update(self.backend_kwargs)

        return xr.open_mfdataset(
            [r.path for r in self.readers],
            engine=self.engine,
            preprocess=preprocess,
            **options,
        )


_READERS = {}


# TODO: Add plugins
@locked
def _readers():
    if not _READERS:
        here = os.path.dirname(__file__)
        for path in os.listdir(here):
            if path.endswith(".py") and path[0] not in ("_", "."):
                name, _ = os.path.splitext(path)
                try:
                    _READERS[name] = import_module(f".{name}", package=__name__).reader
                except Exception as e:
                    warnings.warn(f"Error loading helper {name}: {e}")
    return _READERS


def reader(source, path):

    if os.path.isdir(path):
        from .directory import DirectoryReader

        return DirectoryReader(source, path)

    with open(path, "rb") as f:
        magic = f.read(8)

    for name, r in _readers().items():
        try:
            reader = r(source, path, magic)
            if reader is not None:
                return reader.mutate()
        except Exception as e:
            warnings.warn(f"Error calling reader '{name}': {e}")

    raise ValueError(f"Cannot find a reader for file '{path}' (magic {magic})")
