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
import time
from unittest.mock import patch

import pytest

from climetlab import load_source, settings
from climetlab.core.temporary import temp_directory

LOG = logging.getLogger(__name__)


class OfflineError(Exception):
    pass


class NetworkPatcher:
    def __init__(self):
        self.patcher = patch("socket.socket", side_effect=OfflineError)

    def off(self):
        self.patcher.start()

    def on(self):
        self.patcher.stop()


@pytest.fixture()
def network():
    network = NetworkPatcher()
    yield network
    # network.on() # Teardown cleanup code see https://docs.pytest.org/en/6.2.x/fixture.html


def test_unpack_zip(network):

    network.on()

    try:

        network.off()
        with pytest.raises(OfflineError):
            ds = load_source(
                "url",
                f"https://get.ecmwf.int/test-data/climetlab/input/grib.zip?time={time.time()}",
            )

        network.on()

        with temp_directory() as tmpdir:
            with settings.temporary("cache-directory", tmpdir):
                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/input/grib.zip",
                )
                assert len(ds) == 6, len(ds)

                network.off()  # Make sure we fail if not cached

                # Check cache
                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/input/grib.zip",
                )
                assert len(ds) == 6, len(ds)

                network.on()

                LOG.debug("Use the force")
                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/input/grib.zip",
                    force=True,
                )
                assert len(ds) == 6, len(ds)

                network.off()  # Make sure we fail if not cached

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
        network.on()


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
