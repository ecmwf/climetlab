#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging
import sys

import pytest

from climetlab import load_source, settings
from climetlab.core.temporary import temp_directory

LOG = logging.getLogger(__name__)


class OfflineError(Exception):
    pass


class OfflineRequests:
    def __init__(self):
        import requests as original_requests

        self.original_requests = original_requests
        self.offline = False

    def __getattr__(self, name):
        if self.offline:
            raise OfflineError(name)
        return getattr(self.original_requests, name)


sys.modules["requests"] = OfflineRequests()


def offline(off):
    sys.modules["requests"].offline = off


@pytest.mark.long_test
def test_unpack_zip():

    offline(False)

    try:

        offline(True)
        with pytest.raises(OfflineError):
            ds = load_source(
                "url",
                "https://get.ecmwf.int/test-data/climetlab/input/grib.zip",
                force=True,
            )

        offline(False)

        with temp_directory() as tmpdir:
            with settings.temporary("cache-directory", tmpdir):
                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/input/grib.zip",
                )
                assert len(ds) == 6, len(ds)

                offline(True)  # Make sure we fail if not cached

                # Check cache
                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/input/grib.zip",
                )
                assert len(ds) == 6, len(ds)

                offline(False)

                LOG.debug("Use the force")
                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/input/grib.zip",
                    force=True,
                )
                assert len(ds) == 6, len(ds)

                offline(True)  # Make sure we fail if not cached

                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/input/grib.zip",
                )
                assert len(ds) == 6, len(ds)

                # Again
                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/input/grib.zip",
                )
                assert len(ds) == 6, len(ds)
    finally:
        offline(False)


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
