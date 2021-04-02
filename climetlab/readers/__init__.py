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
