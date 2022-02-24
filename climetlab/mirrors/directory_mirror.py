# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import inspect
import logging
import os
import shutil
from urllib.parse import urlparse

from climetlab.sources.ecmwf_open_data import EODRetriever
from climetlab.sources.file import FileSource
from climetlab.sources.url import Url

from . import BaseMirror, MirrorConnection
from .source_mutator import SourceMutator

LOG = logging.getLogger(__name__)


def strict_init(cls):

    sig = inspect.signature(cls.__init__)

    def check_type(name, value):
        type = sig.parameters[name].annotation
        if type == inspect._empty:
            return
        assert isinstance(value, type), (value, type)

    class Wrapped(cls):
        def __init__(self, mirror, source, *args, **kwargs):
            check_type("mirror", mirror)
            check_type("source", source)
            return super().__init__(mirror, source, *args, **kwargs)

    return Wrapped


class DirectoryMirror(BaseMirror):
    def __init__(self, path, origin_prefix="", **kwargs):
        self.path = path
        self.origin_prefix = origin_prefix
        self.kwargs = kwargs

    def __repr__(self):
        return f"DirectoryMirror({self.path}, {self.kwargs})"

    def connection_for_url(self, source, source_kwargs):
        return DirectoryMirrorConnectionForUrl(self, source, source_kwargs)

    def connection_for_eod(self, source, source_kwargs):
        return DirectoryMirrorConnectionForEODRetriever(self, source, source_kwargs)


class DirectoryMirrorConnection(MirrorConnection):
    def _realpath(self):
        keys = self._to_keys()
        assert isinstance(keys, (list, tuple)), type(keys)
        path = os.path.join(
            self.mirror.path,
            *keys,
        )
        return os.path.realpath(path)

    def contains(self):
        return os.path.exists(self._realpath())


class DirectoryMirrorConnectionForFile(DirectoryMirrorConnection):
    def __init__(self, mirror: DirectoryMirror, source: FileSource, source_kwargs):
        assert isinstance(source, FileSource)
        return super().__init__(mirror, source, source_kwargs)

    def copy(self):
        origin_path = self.source.path
        path = self._realpath()
        LOG.debug(f"Building mirror: cp {origin_path} {path}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.copy2(origin_path, path)

    def mutator(self):
        new_url = "file://" + self._realpath()
        LOG.debug(f"Found mirrored file for {self.source} in {new_url}")
        return SourceMutator("url", new_url)


class DirectoryMirrorConnectionForEODRetriever(DirectoryMirrorConnectionForFile):
    def __init__(self, mirror: DirectoryMirror, source: EODRetriever, source_kwargs):
        assert isinstance(source, EODRetriever)
        return super().__init__(mirror, source, source_kwargs)

    def _to_keys(self):
        request = self.source_kwargs
        keys = []
        for k in request.keys():
            keys.append(k)
            keys.append(str(request[k]))
        return keys


class DirectoryMirrorConnectionForUrl(DirectoryMirrorConnectionForFile):
    def __init__(self, mirror: DirectoryMirror, source: Url, source_kwargs):
        assert isinstance(source, Url)
        return super().__init__(mirror, source, source_kwargs)

    def mutator(self):
        if self.source.url == "file://" + self._realpath():
            return None  # avoid infinite loop
        return super().mutator()

    def contains(self):
        if not self.source.url.startswith(self.mirror.origin_prefix):
            return False
        return super().contains()

    def _to_keys(self):
        url = self.source.url
        if self.mirror.origin_prefix:
            key = url[(len(self.mirror.origin_prefix) + 1) :]
            return ["url", key]

        url = urlparse(url)
        keys = [url.scheme, f"{url.netloc}/{url.path}"]
        return ["url"] + keys
