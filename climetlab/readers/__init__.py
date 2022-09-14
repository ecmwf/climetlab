# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
import weakref
from importlib import import_module

from climetlab.core import Base
from climetlab.decorators import locked

LOG = logging.getLogger(__name__)


class ReaderMeta(type(Base), type(os.PathLike)):
    pass


class Reader(Base, os.PathLike, metaclass=ReaderMeta):

    appendable = False  # Set to True if the data can be appened to and existing file
    binary = True

    def __init__(self, source, path):

        LOG.debug("Reader for %s is %s", path, self.__class__.__name__)

        self._source = weakref.ref(source)
        self.path = path

    @property
    def source(self):
        return self._source()

    @property
    def filter(self):
        return self.source.filter

    @property
    def merger(self):
        return self.source.merger

    def mutate(self):
        # Give a chance to `directory` or `zip` to change the reader
        return self

    def mutate_source(self):
        # The source may ask if it needs to mutate
        return None

    def ignore(self):
        # Used by multi-source
        return False

    def cache_file(self, *args, **kwargs):
        return self.source.cache_file(*args, **kwargs)

    def save(self, path):
        mode = "wb" if self.binary else "w"
        with open(path, mode) as f:
            self.write(f)

    def write(self, f):
        if not self.appendable:
            assert f.tell() == 0
        mode = "rb" if self.binary else "r"
        with open(self.path, mode) as g:
            while True:
                chunk = g.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)

    def __fspath__(self):
        return self.path

    def index_content(self):
        LOG.warning(f"index-content(): Ignoring {self.path}")
        return []


_READERS = {}


# TODO: Add plugins
@locked
def _readers():
    if not _READERS:
        here = os.path.dirname(__file__)
        for path in sorted(os.listdir(here)):

            if path[0] in ("_", "."):
                continue

            if path.endswith(".py") or os.path.isdir(os.path.join(here, path)):

                name, _ = os.path.splitext(path)

                try:
                    module = import_module(f".{name}", package=__name__)
                    if hasattr(module, "reader"):
                        _READERS[name] = module.reader
                        if hasattr(module, "aliases"):
                            for a in module.aliases:
                                assert a not in _READERS
                                _READERS[a] = module.reader
                except Exception:
                    LOG.exception("Error loading reader %s", name)

    return _READERS


def reader(source, path):

    assert isinstance(path, str), source

    if hasattr(source, "reader"):
        reader = source.reader
        LOG.debug("Looking for a reader for %s (%s)", path, reader)
        if callable(reader):
            return reader(source, path)
        if isinstance(reader, str):
            return _readers()[reader.replace("-", "_")](source, path, None, False)

        raise TypeError(
            "Provided reader must be a callable or a string, not %s" % type(reader)
        )

    if os.path.isdir(path):
        from .directory import DirectoryReader

        return DirectoryReader(source, path).mutate()
    LOG.debug("Reader for %s", path)

    with open(path, "rb") as f:
        magic = f.read(8)

    LOG.debug("Looking for a reader for %s (%s)", path, magic)

    for deeper_check in (False, True):
        # We do two passes, the second one
        # allow the plugin to look deeper in the file
        for name, r in _readers().items():
            reader = r(source, path, magic, deeper_check)
            if reader is not None:
                return reader.mutate()

    from .unknown import Unknown

    return Unknown(source, path, magic)
