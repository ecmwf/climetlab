#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import time

import pytest

from climetlab import load_source
from climetlab.indexing import PerUrlIndex

CML_BASEURL_S3 = "https://object-store.os-api.cci1.ecmwf.int/climetlab"
CML_BASEURL_CDS = "https://datastore.copernicus-climate.eu/climetlab"
CML_BASEURL_GET = "https://get.ecmwf.int/repository/test-data/climetlab"
CML_BASEURLS = [CML_BASEURL_S3, CML_BASEURL_GET, CML_BASEURL_CDS]


def check(source, i, ref):
    field = source[i]
    n = field.to_numpy()
    mean = n.mean()
    assert abs(mean - ref) < 1e-6, (mean, ref, field)


REQUEST_1 = {
    "domain": "g",
    "levtype": "pl",
    "levelist": "850",
    "date": "19970228",
    "time": "2300",
    "step": "0",
    "param": "r",
    "class": "ea",
    "type": "an",
    "stream": "oper",
    "expver": "0001",
    #
    "n": ["1", "2"],
}


@pytest.mark.long_test
@pytest.mark.download
@pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_indexed_urls_deprecated(baseurl):
    PER_URL_INDEX = PerUrlIndex(baseurl + "/test-data/input/indexed-urls/large_grib_{n}.grb")
    source = load_source("indexed-urls", PER_URL_INDEX, REQUEST_1)
    check(source, 0, 49.86508481081071)
    ds = source.to_xarray()
    assert abs(ds["r"].mean() - 49.86508560180664) < 1e-6


@pytest.mark.long_test
@pytest.mark.download
@pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_indexed_urls(baseurl):
    source = load_source(
        "indexed-urls",
        baseurl + "/test-data/input/indexed-urls/large_grib_{n}.grb",
        REQUEST_1,
    )
    check(source, 0, 49.86508481081071)
    ds = source.to_xarray()
    assert abs(ds["r"].mean() - 49.86508560180664) < 1e-6


@pytest.mark.long_test
@pytest.mark.download
@pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_per_url_index(baseurl):
    request = dict(param="r", time="1000", date="19970101")
    load_source(
        "indexed-urls",
        f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb",
        request,
    )


@pytest.mark.long_test
@pytest.mark.download
# @pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_per_url_index_2():
    baseurl = CML_BASEURL_S3
    request = dict(param="cin", date="20211125", step="6", number=["1", "3"])
    load_source("indexed-urls", f"{baseurl}/test-data/big.grib", request)


def retrieve(pattern, request, range_method=None, **kwargs):
    print("--------")
    print("range_method", range_method)
    print("Request=", request)

    now = time.time()
    load_source(  # noqa F841
        "indexed-urls",
        pattern,
        request,
        range_method=range_method,
        **kwargs,
    )
    elapsed = time.time() - now
    return elapsed


def dev():
    baseurl = CML_BASEURL_S3
    pattern = f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb"

    request = dict(param="r")
    retrieve(pattern, request)

    request = dict(param="r", time="1000")
    retrieve(pattern, request)

    request = dict(date="19970101")
    retrieve(pattern, request)

    request = dict(param="r", time="1000", date="19970101")
    retrieve(pattern, request)


def timing():
    baseurl = CML_BASEURL_S3
    baseurl = CML_BASEURL_CDS
    pattern = f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb"

    sizes = ["sharp(1,1)", "auto", "cluster"]
    sizes = []
    for r in range(11, 24):  # from 2k to 8M
        sizes.append(f"blocked({2 ** r})")

    report = {}
    for request in [
        dict(param="r"),
        dict(param="r", time="1000"),
        dict(date="19970101"),
        dict(param="r", time="1000", date="19970101"),
    ]:
        times = []
        for n in sizes:
            try:
                elapsed = retrieve(pattern, request, range_method=n, force=True)
            except Exception as e:
                print(e)
                times.append(-1)
                continue
            if n is None:
                n = 0
            if n == "auto":
                n = -1
            if n == "cluster":
                n = 1
            if n == "sharp":
                n = -2
            times.append((round(elapsed * 10) / 10.0, n))

        report[tuple(request.items())] = request, sorted(times)

    for k, v in report.items():
        print(k)
        print(v)


@pytest.mark.long_test
@pytest.mark.download
def test_grib_index_eumetnet():
    request = {
        "param": "2ti",
        "date": "20171228",
        "step": ["0-24", "24-48", "48-72", "72-96", "96-120", "120-144", "144-168"],
        # Parameters passed to the filename mangling
        "url": "https://object-store.os-api.cci1.ecmwf.int/eumetnet-postprocessing-benchmark-training-dataset/",
        "month": "12",
        "year": "2017",
    }
    PATTERN = "{url}data/fcs/efi/" "EU_forecast_efi_params_{year}-{month}_0.grb"
    ds = load_source("indexed-urls", PATTERN, request)
    assert len(ds) == 7, len(ds)
    check(ds, 0, -0.16334878510300832)
    check(ds, 1, -0.06413754859021915)
    check(ds, 2, 0.23404628380396034)
    check(ds, 3, 0.3207112379535552)
    xds = ds.to_xarray()
    print(xds)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
    # test_per_url_index(CML_BASEURL_CDS)
    # test_indexed_s3(CML_BASEURL_S3)
    # timing()
    # from climetlab.testing import main

    # test_grib_index_eumetnet()
