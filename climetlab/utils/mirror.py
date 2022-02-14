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

LOG = logging.getLogger(__name__)


class UrlMirror:
    def __init__(self, redirections):
        self.redirections = redirections

    def build_mirror_url(self, url):
        origin, copy = self.redirections.split(" ")
        new = url.replace(origin, copy)
        return new

    def __call__(self, url):
        new = self.build_mirror_url(url)

        if os.path.exists(new):
            LOG.info("Mirror found at %s", new)
            return new

        if new.startswith("file://") and os.path.exists(new.replace("file://", "")):
            LOG.info("Mirror found at %s", new)
            return new

        LOG.debug("Mirror not found at %s for %s", new, url)
        return url

    def build_mirror(self, path, url):
        new = self.build_mirror_url(url)
        assert new.startswith(
            "file://"
        ), f"Only building file mirror are supported ({new})"
        new = new[len("file://") :]
        if os.path.exists(new):
            return
        LOG.info(f"Building mirror: {new}")
        os.makedirs(os.path.dirname(new), exist_ok=True)
        shutil.copy2(path, new)


global _MIRROR_WRITER
_MIRROR_WRITER = None


class prefetch:
    def __init__(self, directory):
        global _MIRROR_WRITER
        _MIRROR_WRITER = UrlMirror(f"https:// file://{directory}/")

    def __enter__(self):
        pass

    def __exit__(self, *args, **kwargs):
        global _MIRROR_WRITER
        _MIRROR_WRITER = None


def mirror_writer():
    return _MIRROR_WRITER


# TODO: move this to another file
MIRROR_ENV_VAR = os.environ.get("CLIMETLAB_MIRROR")
# export CLIMETLAB_MIRROR='https://storage.ecmwf.europeanweather.cloud file:///data/mirror/https/storage.ecmwf.europeanweather.cloud' # noqa

if MIRROR_ENV_VAR:
    DEFAULT_MIRROR = UrlMirror(MIRROR_ENV_VAR)
else:
    DEFAULT_MIRROR = None
