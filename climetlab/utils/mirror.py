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

import climetlab as cml

LOG = logging.getLogger(__name__)

global _MIRRORS


class SourceMutator:
    def __init__(self, source):
        self.source = source

    def mutate_source(self):
        return self.source


class Mirrors(list):
    def query_mirrors(self, source):
        self.warn_unsupported()
        mutators = []
        for mirror in self:
            assert isinstance(mirror, BaseMirror), mirror
            mutator = mirror.to_mirror_if_exists(source)
            if mutator is not None:
                assert isinstance(mutator, SourceMutator), mutator
            mutators.append(mutator)
        return self, mutators

    def warn_unsupported(self):
        if len(self) <= 1:
            return
        for m in self:
            if m._prefetch:
                LOG.error("Using prefetch with multiple mirrors is not supported.")
                raise Exception(
                    "Using prefetch with multiple mirrors is not supported."
                )
        return


class BaseMirror:

    _prefetch = False

    def __enter__(self):
        self.activate(prefetch=self._prefetch)
        return self

    def __exit__(self, *args, **kwargs):
        self.deactivate()

    def prefetch(self):
        self._prefetch = True
        return self

    def activate(self, prefetch=False):
        self._prefetch = prefetch
        global _MIRRORS
        _MIRRORS.append(self)

    def deactivate(self):
        self._prefetch = False
        global _MIRRORS
        _MIRRORS.remove(self)

    def contains(self, source):
        item = Item(self, source)
        value = self.contains_item(item)
        assert value in [True, False], value
        return value

    def to_mirror_if_exists(self, source):
        item = Item(self, source)

        if self.contains_item(item):
            LOG.debug(f"Found mirrored file for {item}")
            new_url = self.item_to_new_url(item)
            new_source = cml.load_source("url", new_url)
            return SourceMutator(new_source)
        else:
            LOG.debug(f"Cannot find mirrored file for {item}.")
            return None

    def build_copy_if_needed(self, source, path):
        if not self._prefetch:
            LOG.debug(
                f"Mirror {self} does not build copy of {source} because prefetch=False."
            )
            return

        item = Item(self, source)

        if self.contains_item(item):
            LOG.debug(f"OK, mirrored file already exists {item}")
            return

        self.build_copy(item, path)

    def contains_item(self, item):
        raise NotImplementedError()

    def build_copy(self, source, path):
        raise NotImplementedError()

    def item_to_new_url(self, item):
        # TODO: this should be item_to_new_source
        raise NotImplementedError()

    def repr_item(self, item):
        return ""


class Mirror(BaseMirror):
    # TODO: build mirror from json config
    pass


class EmptyMirror(BaseMirror):
    name = "empty_mirror"

    def contains_item(self, item):
        return False

    def build_copy(self, source, path):
        return


class Item:
    def __init__(self, mirror, source):
        self.source = source
        self.mirror = mirror

        self.keys = self.source.get_mirror_keys()

    @property
    def key(self):
        return self.keys["source_key"]

    @property
    def source_name(self):
        return self.keys["source_name"]

    @property
    def mirror_name(self):
        return self.mirror.name

    def __repr__(self):
        rep = self.mirror.repr_item(self)
        return f"Item({self.source_name}={self.key}, {self.mirror_name}={rep})"


class DirectoryMirror(BaseMirror):
    name = "directory_mirror"

    def __init__(self, path, origin_prefix=None, **kwargs):
        self.path = path
        self.origin_prefix = origin_prefix
        self.kwargs = kwargs

    def __repr__(self):
        return f"DirectoryMirror({self.path}, {self.kwargs})"

    def item_to_path(self, item):
        key = item.key
        if self.origin_prefix:
            if not key.startswith(self.origin_prefix):
                return None
            key = key[(len(self.origin_prefix) + 1) :]
        path = os.path.join(
            self.path,
            item.source_name,
            key,
        )
        return os.path.realpath(path)

    def item_to_new_url(self, item):
        path = self.item_to_path(item)
        assert path is not None, item
        return "file://" + path

    def contains_item(self, item):
        path = self.item_to_path(item)
        if path is None:
            return False
        return os.path.exists(path)

    def build_copy(self, item, path):
        new = self.item_to_path(item)

        if new is None:
            LOG.debug(f"Mirror {self} cannot build {item}")
            return

        LOG.info(f"Building mirror for {item}: cp {path} {new}")
        os.makedirs(os.path.dirname(new), exist_ok=True)
        shutil.copy2(path, new)

    def repr_item(self, item):
        return self.item_to_path(item)


def query_mirrors(source):
    global _MIRRORS
    return _MIRRORS.query_mirrors(source)


def _reset_mirrors(use_env_var):
    global _MIRRORS
    _MIRRORS = Mirrors()
    # _MIRRORS.append(EmptyMirror())
    if not use_env_var:
        return

    env_var = os.environ.get("CLIMETLAB_MIRROR")
    if " ":
        # export CLIMETLAB_MIRROR='https://storage.ecmwf.europeanweather.cloud file:///data/mirror/https/storage.ecmwf.europeanweather.cloud' # noqa
        LOG.warning(
            "Deprecation warning:  using CLIMETLAB_MIRROR environment variable string to define a mirror is deprecated."
        )
        origin_prefix, path = env_var.split(" ")
        mirror = DirectoryMirror(path=path, origin_prefix=origin_prefix)
    else:
        mirror = DirectoryMirror(path=env_var)
    _MIRRORS.append(mirror)


def get_mirrors():
    global _MIRRORS
    return _MIRRORS


_reset_mirrors(use_env_var=True)
