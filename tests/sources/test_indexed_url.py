#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import pytest
from test_indexed_urls import CML_BASEURL_CDS  # noqa: F401
from test_indexed_urls import CML_BASEURL_GET  # noqa: F401
from test_indexed_urls import CML_BASEURL_S3  # noqa: F401
from test_indexed_urls import CML_BASEURLS

import climetlab as cml
from climetlab import settings
from climetlab.core.temporary import temp_directory


@pytest.mark.long_test
@pytest.mark.parametrize("baseurl", CML_BASEURLS)
@pytest.mark.parametrize("index_type", ["json", "sql"])
def test_global_index(index_type, baseurl):
    with temp_directory() as tmpdir:
        with settings.temporary():
            settings.set("cache-directory", tmpdir)

            print(f"{baseurl}/test-data/input/indexed-urls/global_index.index")
            s = cml.load_source(
                "indexed-url",
                f"{baseurl}/test-data/input/indexed-urls/global_index.index",
                # baseurl=f"{baseurl}/test-data/input/indexed-urls",
                param="r",
                time=["1000", "1200", "1800"],
                date="19970101",
                _index_type=index_type,
            )
            assert len(s) == 3, len(s)
            assert s[0].metadata("short_name") == "r"
            date = s[0].metadata("date")
            assert str(date) == "19970101", date

            mean = float(s.to_xarray()["r"].mean())
            assert abs(mean - 70.34426879882812) < 0.0000001, mean


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
    # test_global_index("json", CML_BASEURL_S3)
