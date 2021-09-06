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


class UrlMirror:
    def __init__(self, redirections):
        self.redirections = redirections

    def __call__(self, url):
        origin, copy = self.redirections.split(" ")
        new = url.replace(origin, copy)

        if os.path.exists(new):
            LOG.info("Mirror found at %s", new)
            return new

        if new.startswith("file://") and os.path.exists(new.replace("file://", "")):
            LOG.info("Mirror found at %s", new)
            return new

        LOG.debug("Mirror not found at %s for %s", new, url)
        return url


# TODO: move this to another file
MIRROR_ENV_VAR = os.environ.get("CLIMETLAB_MIRROR")
# export CLIMETLAB_MIRROR='https://storage.ecmwf.europeanweather.cloud file:///data/mirror/https/storage.ecmwf.europeanweather.cloud' # noqa

if MIRROR_ENV_VAR:
    DEFAULT_MIRROR = UrlMirror(MIRROR_ENV_VAR)
else:
    DEFAULT_MIRROR = None
