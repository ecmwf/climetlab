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
from test_indexing_source_indexed_urls import (
    CML_BASEURL_CDS,
    CML_BASEURL_GET,
    CML_BASEURL_S3,
    CML_BASEURLS,
)

import climetlab as cml
from climetlab import settings
from climetlab.core.temporary import temp_directory


@pytest.mark.long_test
@pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_global_index(baseurl):
    with temp_directory() as tmpdir:
        with settings.temporary():
            settings.set("cache-directory", tmpdir)

            print(f"{baseurl}/test-data/input/indexed-urls/global_index.index")
            s = cml.load_source(
                "indexed-url",
                f"{baseurl}/test-data/input/indexed-urls/global_index.index",
                baseurl=f"{baseurl}/test-data/input/indexed-urls",
                param="r",
                time="1000",
                date="19970101",
                index_type="json",
            )
            assert len(s) == 4
            assert s[0].metadata("short_name") == "r"
            assert s[0].metadata("time") == "1000"
            assert s[0].metadata("date") == "19970101"

            s.to_xarray()


if __name__ == "__main__":
    from climetlab.testing import main

    # main(__file__)
    test_global_index(CML_BASEURL_S3)
