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


class DirectoryMirrorForUrl(XMirrorForY):
    def _mutator(self):
        new_url = "file://" + self.mirror._realpath(self.source, **self.source_kwargs)
        source_url = self.source.url
        if new_url != source_url:
            LOG.debug(f"Found mirrored file for {source_url} in {new_url}")
            return SourceMutator("url", new_url)
        return None

    def contains(self):
        url = self.source.url
        if not url.startswith(self.mirror.origin_prefix):
            return False
        path = self.mirror._realpath(self.source, **self.source_kwargs)
        return os.path.exists(path)

    def _copy(self):
        source_path = self.source.path
        path = self.mirror._realpath(self.source, **self.source_kwargs)
        LOG.info(f"Building mirror for {self.source}: cp {source_path} {path}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.copy2(source_path, path)


class DirectoryMirror(BaseMirror):
    def __init__(self, path, origin_prefix="", **kwargs):
        self.path = path
        self.origin_prefix = origin_prefix
        self.kwargs = kwargs

    def __repr__(self):
        return f"DirectoryMirror({self.path}, {self.kwargs})"

    def mirror_interface_for_url(self, source, source_kwargs):
        return DirectoryMirrorForUrl(self, source, source_kwargs)

    def _realpath(self, source, **kwargs):
        keys = self._url_to_keys(source, **kwargs)
        assert isinstance(keys, (list, tuple)), type(keys)
        path = os.path.join(
            self.path,
            *keys,
        )
        return os.path.realpath(path)

    def _url_to_keys(self, source, **kwargs):
        url = source.url
        if self.origin_prefix:
            key = url[(len(self.origin_prefix) + 1) :]
            return ["url", key]

        url = urlparse(url)
        keys = [url.scheme, f"{url.netloc}/{url.path}"]
        return ["url"] + keys
