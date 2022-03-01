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

LOG = logging.getLogger(__name__)

global _MIRRORS


class MirrorConnection:
    def __init__(self, mirror, source):
        self.mirror = mirror
        self.source = source

    def get_file(self, create, args):
        if self.resource():
            LOG.debug(
                f"Found a copy of {self.source} in mirror {self.mirror}: {self.resource()}."
            )
            return self.resource()
        if not self.mirror._prefetch:
            LOG.debug(f"No copy of {self.source} into {self.mirror}: prefetch=False.")
            return None
        LOG.info(f"Building mirror for {self.source} in mirror {self.mirror}.")
        return self.create_copy(create, args)

    def resource(self):
        LOG.info(f"Not implemented. {self.source} not in mirror {self.mirror}.")
        return None

    def create_copy(self, create, args):
        LOG.info(
            f"Not implemented. Not creating anything for {self.source} in mirror {self.mirror}."
        )
        return None


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

    # convenience method for testing purposes
    def contains(self, source):
        return source.connect_to_mirror(self).resource() is not None

    def connection_for_url(self, source, *args, **kwargs):
        return None

    def connection_for_eod(self, source, *args, **kwargs):
        return None


class Mirror(BaseMirror):
    # TODO: build mirror from json config
    pass


def build_mirror_from_env_var():
    from .directory_mirror import DirectoryMirror

    env_var = os.environ.get("CLIMETLAB_MIRROR")
    if not env_var:
        return None

    if " " in env_var:
        # export CLIMETLAB_MIRROR='https://storage.ecmwf.europeanweather.cloud file:///data/mirror/https/storage.ecmwf.europeanweather.cloud' # noqa
        LOG.warning(
            "Deprecation warning: this use of CLIMETLAB_MIRROR environment variable"
            " to define a mirror will be deprecated."
        )
        origin_prefix, path = env_var.split(" ")
        # assert is_url(origin_prefix), "Cannot parse CLIMETLAB_MIRROR={env_var}."
        # assert is_url(path), "Cannot parse CLIMETLAB_MIRROR={env_var}."
        return DirectoryMirror(path=path, origin_prefix=origin_prefix)

    return DirectoryMirror(path=env_var)


def get_active_mirrors():
    global _MIRRORS
    return _MIRRORS


def _reset_mirrors(use_env_var):
    global _MIRRORS
    _MIRRORS = []

    if use_env_var:
        mirror = build_mirror_from_env_var()
        if mirror:
            _MIRRORS.append(mirror)


_reset_mirrors(use_env_var=True)
