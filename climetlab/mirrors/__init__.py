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


class XMirrorForY:
    def __init__(self, mirror, source, source_kwargs):
        self.mirror = mirror
        self.source = source
        self.source_kwargs = source_kwargs

    def mutator(self):
        if not self.contains():
            LOG.debug(f"Cannot find a copy of {self.source} in mirror {self.mirror}.")
            return None
        mutator = self._mutator()
        if not mutator:
            LOG.debug(
                f"Not redirecting {self.source} to its copy in mirror {self.mirror}."
            )
            return None
        LOG.debug(f"Found a copy of {self.source} in mirror {self.mirror}.")
        return mutator

    def copy(self):
        if not self.mirror._prefetch:
            LOG.debug(f"No copy of {self.source} into {self.mirror}: prefetch=False.")
            return
        if self.contains():
            LOG.debug(f"No copy of {self.source} into {self.mirror}: already contains.")
            return
        self._copy()

    def _mutator(self):
        LOG.debug(f"No mirroring of {self.source} into {self.mirror}: not implemented.")
        return None

    def _copy(self):
        LOG.debug(f"No copy of {self.source} into {self.mirror}: not implemented.")
        return

    def contains(self):
        return False


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

    # Convenience method used for testing.
    def contains(self, source, source_kwargs):
        connection = source.connect_to_mirror(self, {})
        if not connection:
            return False
        return connection.contains()

    # We could add this if needed.
    # def connect_to_source(self, source, source_kwargs):
    #    return source.connect_to_mirror(self, source_kwargs)


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


def get_mirrors():
    global _MIRRORS
    lst = _MIRRORS
    if len(lst) > 1 and any([m._prefetch for m in lst]):
        LOG.error("Using prefetch with multiple mirrors is not supported.")
        raise Exception(f"Unsupported use of prefetch with multiple mirrors {lst}.")
    return _MIRRORS


def _reset_mirrors(use_env_var):
    global _MIRRORS
    _MIRRORS = []

    if use_env_var:
        mirror = build_mirror_from_env_var()
        if mirror:
            _MIRRORS.append(mirror)


_reset_mirrors(use_env_var=True)
