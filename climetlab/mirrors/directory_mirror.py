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
import shutil
from urllib.parse import urlparse

from . import BaseMirror, XMirrorForY
from .source_mutator import SourceMutator

LOG = logging.getLogger(__name__)


class DirectoryMirrorForY(XMirrorForY):
    def _realpath(self):
        keys = self._to_keys()
        assert isinstance(keys, (list, tuple)), type(keys)
        path = os.path.join(
            self.mirror.path,
            *keys,
        )
        return os.path.realpath(path)


class DirectoryMirrorForUrl(DirectoryMirrorForY):
    def _mutator(self):
        new_url = "file://" + self._realpath()
        source_url = self.source.url
        if new_url != source_url:
            LOG.debug(f"Found mirrored file for {source_url} in {new_url}")
            return SourceMutator("url", new_url)
        return None

    def contains(self):
        if not self.source.url.startswith(self.mirror.origin_prefix):
            return False
        return os.path.exists(self._realpath())

    def _copy(self):
        source_path = self.source.path
        path = self._realpath()
        LOG.info(f"Building mirror for {self.source}: cp {source_path} {path}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.copy2(source_path, path)

    def _to_keys(self):
        url = self.source.url
        if self.mirror.origin_prefix:
            key = url[(len(self.mirror.origin_prefix) + 1) :]
            return ["url", key]

        url = urlparse(url)
        keys = [url.scheme, f"{url.netloc}/{url.path}"]
        return ["url"] + keys


class DirectoryMirror(BaseMirror):
    def __init__(self, path, origin_prefix="", **kwargs):
        self.path = path
        self.origin_prefix = origin_prefix
        self.kwargs = kwargs

    def __repr__(self):
        return f"DirectoryMirror({self.path}, {self.kwargs})"

    def connection_for_url(self, source, source_kwargs):
        return DirectoryMirrorForUrl(self, source, source_kwargs)
