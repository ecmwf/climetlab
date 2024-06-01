#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json

import pytest
from test_indexed_urls import CML_BASEURL_CDS  # noqa: F401
from test_indexed_urls import CML_BASEURL_GET  # noqa: F401
from test_indexed_urls import CML_BASEURL_S3  # noqa: F401
from test_indexed_urls import CML_BASEURLS

import climetlab as cml
from climetlab.scripts.main import CliMetLabApp


@pytest.mark.skip(reason="Global index not supported.")
@pytest.mark.long_test
@pytest.mark.download
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


def check_line_2(line2):
    for k, v in {
        "domain": "g",
        "levtype": "pl",
        "levelist": 500,
        "date": 19970101,
        "time": 200,
        "step": 0,
        "param": "z",
        "class": "ea",
        "type": "an",
        "stream": "oper",
        "expver": "0001",
        "_offset": 46716,
        "_length": 23358,
        "_param_id": "129",
    }.items():
        assert line2[k] == v, (line2[k], v)


@pytest.mark.parametrize("baseurl", CML_BASEURLS)
# @pytest.mark.parametrize("baseurl", [CML_BASEURL_S3])
@pytest.mark.download
def test_cli_index_url(baseurl, capsys):
    app = CliMetLabApp()
    app.onecmd(f"index_url {baseurl}/test-data/input/indexed-urls/large_grib_1.grb")
    out, err = capsys.readouterr()
    lines = out.split("\n")
    if "error" in err.lower():
        assert False, err

    assert len(lines) == 4465, len(lines)
    line2 = json.loads(lines[2])
    check_line_2(line2)
    assert "_path" not in line2


# @pytest.mark.parametrize("baseurl", CML_BASEURLS)
@pytest.mark.parametrize("baseurl", [CML_BASEURL_S3])
@pytest.mark.download
def test_cli_index_urls(baseurl, capsys):
    app = CliMetLabApp()
    app.onecmd(f"index_urls --baseurl {baseurl}/test-data/input/indexed-urls large_grib_1.grb large_grib_2.grb")
    out, err = capsys.readouterr()
    lines = out.split("\n")
    if "error" in err.lower():
        assert False, err

    assert len(lines) == 8497, lines[0:10]
    line2 = json.loads(lines[2])
    check_line_2(line2)
    assert line2["_path"] == "large_grib_1.grb"


# @pytest.mark.parametrize("baseurl", CML_BASEURLS)
@pytest.mark.parametrize("baseurl", [CML_BASEURL_S3])
@pytest.mark.download
def test_cli_index_urls_full_url(baseurl, capsys):
    app = CliMetLabApp()
    app.onecmd(
        (
            f"index_urls {baseurl}/test-data/input/indexed-urls/large_grib_1.grb"
            " "
            f"{baseurl}/test-data/input/indexed-urls/large_grib_2.grb"
        )
    )
    out, err = capsys.readouterr()
    lines = out.split("\n")
    if "error" in err.lower():
        assert False, err

    assert len(lines) == 8497
    line2 = json.loads(lines[2])
    check_line_2(line2)
    assert line2["_path"] == f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb"


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
    # test_global_index("indexed-url-with-json-index", CML_BASEURL_S3)
    test_cli_index_url
