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
from climetlab.scripts.main import CliMetLabApp
from climetlab.core.temporary import temp_directory, temp_file


@pytest.mark.long_test
@pytest.mark.parametrize("baseurl", CML_BASEURLS)
@pytest.mark.parametrize("source_name", ["indexed-url", "indexed-url-with-json-index"])
def test_global_index(source_name, baseurl):
    # with temp_directory() as tmpdir:
    #    with settings.temporary():
    #        settings.set("cache-directory", tmpdir)

    print(f"{baseurl}/test-data/input/indexed-urls/global_index.index")
    s = cml.load_source(
        source_name,
        f"{baseurl}/test-data/input/indexed-urls/global_index.index",
        # baseurl=f"{baseurl}/test-data/input/indexed-urls",
        param="r",
        time=["1000", "1200", "1800"],
        date="19970101",
    )

    assert len(s) == 3, len(s)
    assert s[0].metadata("short_name") == "r"
    date = s[0].metadata("date")
    assert str(date) == "19970101", date

    mean = float(s.to_xarray()["r"].mean())
    assert abs(mean - 70.34426879882812) < 0.0000001, mean


#  climetlab index_urls $BASEURL/large_grib_1.grb > large_grib_1.grb.index
#  climetlab index_gribs $BASEURL/large_grib_2.grb > large_grib_2.grb.index
#  climetlab index_gribs large_grib_1.grb large_grib_2.grb --baseurl $BASEURL > global_index.index
@pytest.mark.parametrize("baseurl", CML_BASEURLS)
# @pytest.mark.parametrize("baseurl", [CML_BASEURL_S3])
def test_cli_index_url(baseurl):
    app = CliMetLabApp()
    app.onecmd(f"index_url {baseurl}/test-data/input/indexed-urls/large_grib_1.grb")


@pytest.mark.parametrize("baseurl", CML_BASEURLS)
# @pytest.mark.parametrize("baseurl", [CML_BASEURL_S3])
def test_cli_index_url(baseurl):
    app = CliMetLabApp()
    tmp = temp_file()
    app.onecmd(f"index_urls -o {tmp.path} --baseurl {baseurl}/test-data/input/indexed-urls large_grib_1.grb large_grib_2.grb")
    


if __name__ == "__main__":
    from climetlab.testing import main

    # main(__file__)
    test_global_index("indexed-url-with-json-index", CML_BASEURL_S3)
