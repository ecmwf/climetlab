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

from climetlab import load_source, settings
from climetlab.core.temporary import temp_directory
from climetlab.sources.url import offline

LOG = logging.getLogger(__name__)


def test_unpack_zip():
    try:
        with temp_directory() as tmpdir:
            with settings.temporary("cache-directory", tmpdir):
                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/grib.zip",
                )
                assert len(ds) == 6, len(ds)

                offline(True)  # Make sure we fail if not cached

                # Check cache
                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/grib.zip",
                )
                assert len(ds) == 6, len(ds)

                offline(False)

                LOG.debug("Use the force")
                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/grib.zip",
                    force=True,
                )
                assert len(ds) == 6, len(ds)

                offline(True)  # Make sure we fail if not cached

                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/grib.zip",
                )
                assert len(ds) == 6, len(ds)

                # Again
                ds = load_source(
                    "url",
                    "https://get.ecmwf.int/test-data/climetlab/grib.zip",
                )
                assert len(ds) == 6, len(ds)
    finally:
        offline(False)


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
