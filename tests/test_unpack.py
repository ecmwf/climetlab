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

import pytest

from climetlab import load_source
from climetlab import settings
from climetlab.core.temporary import temp_directory
from climetlab.testing import OfflineError
from climetlab.testing import network_off

LOG = logging.getLogger(__name__)


@pytest.mark.download
@pytest.mark.small_download
def test_unpack_zip():
    TEST_URL = "https://get.ecmwf.int/test-data/climetlab/input/grib.zip"

    # Make sure we fail if not cached
    with pytest.raises(OfflineError), network_off():
        ds = load_source("url", f"{TEST_URL}?time={time.time()}")

    with temp_directory() as tmpdir:
        with settings.temporary("cache-directory", tmpdir):
            ds = load_source("url", TEST_URL)
            assert len(ds) == 6, len(ds)

            with network_off():
                # Check cache is used
                ds = load_source("url", TEST_URL)
                assert len(ds) == 6, len(ds)

            with pytest.raises(OfflineError), network_off():
                # check force
                ds = load_source("url", TEST_URL, force=True)
                assert len(ds) == 6, len(ds)

            ds = load_source("url", TEST_URL, force=True)
            assert len(ds) == 6, len(ds)

            with network_off():
                ds = load_source("url", TEST_URL)
                assert len(ds) == 6, len(ds)

                # Again
                ds = load_source("url", TEST_URL)
                assert len(ds) == 6, len(ds)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
