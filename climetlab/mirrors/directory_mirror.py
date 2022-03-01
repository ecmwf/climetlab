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
from urllib.parse import urlparse

from climetlab.sources.ecmwf_open_data import EODRetriever
from climetlab.sources.file import FileSource
from climetlab.sources.url import Url

from . import BaseMirror, MirrorConnection

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
    def __init__(self, path, origin_prefix=""):
        self.path = path
        self.origin_prefix = origin_prefix

    def __repr__(self):
        return f"DirectoryMirror({self.path}, {self.origin_prefix})"

    def connection_for_url(self, source, url, parts):
        if not url.startswith(self.origin_prefix):
            return None
        if parts:
            # return DirectoryMirrorConnectionForUrlWithPargs(self, source, url, parts)
            return None
        return DirectoryMirrorConnectionForUrl(self, source)

    def connection_for_eod(self, source):
        return DirectoryMirrorConnectionForEODRetriever(self, source)


class DirectoryMirrorConnection(MirrorConnection):
    def _realpath(self):
        keys = self._to_keys()
        assert isinstance(keys, (list, tuple)), type(keys)
        path = os.path.join(
            self.mirror.path,
            *keys,
        )
        return os.path.realpath(path)


class DirectoryMirrorConnectionForFile(DirectoryMirrorConnection):
    def __init__(self, mirror: DirectoryMirror, source: FileSource):
        assert isinstance(source, FileSource)
        return super().__init__(mirror, source)

    def resource(self):
        path = self._realpath()
        if os.path.exists(path):
            return path
        else:
            return None

    def create_copy(self, create, args):
        path = self._realpath()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        create(path, args)
        return path


class DirectoryMirrorConnectionForEODRetriever(DirectoryMirrorConnectionForFile):
    def __init__(self, mirror: DirectoryMirror, source: EODRetriever):
        assert isinstance(source, EODRetriever)
        return super().__init__(mirror, source)

    def _to_keys(self):
        request = self.source.source_kwargs
        keys = []
        for k in request.keys():
            keys.append(k)
            keys.append(str(request[k]))
        return keys


class DirectoryMirrorConnectionForUrl(DirectoryMirrorConnectionForFile):
    def __init__(self, mirror: DirectoryMirror, source: Url):
        assert isinstance(source, Url)
        return super().__init__(mirror, source)

    def _to_keys(self):
        url = self.source.url
        if self.mirror.origin_prefix:
            key = url[(len(self.mirror.origin_prefix) + 1) :]
            return ["url", key]

        url = urlparse(url)
        keys = [url.scheme, f"{url.netloc}/{url.path}"]
        return ["url"] + keys
