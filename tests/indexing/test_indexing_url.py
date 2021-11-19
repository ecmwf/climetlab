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
from climetlab.core.statistics import collect_statistics, retrieve_statistics
from climetlab.datasets import Dataset
from climetlab.decorators import normalize
from climetlab.indexing import GlobalIndex, PerUrlIndex

CML_BASEURL_S3 = "https://storage.ecmwf.europeanweather.cloud/climetlab"
CML_BASEURL_CDS = "https://datastore.copernicus-climate.eu/climetlab"
CML_BASEURLS = [CML_BASEURL_S3, CML_BASEURL_CDS]

# index file has been created with :
# climetlab index_gribs --baseurl "https://storage.ecmwf.europeanweather.cloud/benchmark-dataset" \
#           data/ana/pressure/EU_analysis_pressure_params_1997-01.grb > eumetnet.index
# climetlab index_gribs --baseurl "https://storage.ecmwf.europeanweather.cloud/benchmark-dataset" \
#           data/ana/pressure/EU_analysis_pressure_params_1997-02.grb >> eumetnet.index


@pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_indexed_s3(baseurl):
    PER_URL_INDEX = PerUrlIndex(
        baseurl + "/test-data/input/indexed-urls/large_grib_{n}.grb"
    )

    class Mydataset(Dataset):
        @normalize(
            "param",
            ["133", "157", "130", "131", "132", "129"],
            aliases="eumetnet_aliases.yaml",
            # multiple=True,
        )
        def __init__(self, option="abc", **request):
            self.source = load_source("indexed-urls", PER_URL_INDEX, request)

    a = Mydataset(
        **{
            "domain": "g",
            "levtype": "pl",
            "levelist": "850",
            "date": "19970228",
            "time": "2300",
            "step": "0",
            "param": "r",  # "param": "157",
            "class": "ea",
            "type": "an",
            "stream": "oper",
            "expver": "0001",
            #
            "n": ["1", "2"],
        }
    )
    ds = a.to_xarray()
    assert abs(ds["r"].mean() - 49.86508560180664) < 1e-6


def retrieve_and_check(index, request, range_method, **kwargs):
    print("--------")
    parts = index.lookup_request(request)
    print("range_method", range_method)
    print("REQUEST", request)
    for url, p in parts:
        total = len(index.get_backend(url).entries)
        print(f"PARTS: {len(p)}/{total} parts in {url}")

    now = time.time()
    s = load_source("indexed-urls", index, request, range_method=range_method, **kwargs)
    elapsed = time.time() - now
    print("ELAPSED", elapsed)
    try:
        paths = [s.path]
    except AttributeError:
        paths = [p.path for p in s.sources]

    for path in paths:
        # check that the downloaded gribs match the request
        for grib in load_source("file", path):
            for k, v in request.items():
                assert str(grib._get(k)) == str(v), (grib._get(k), v)
    return elapsed


@pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_global_index(baseurl):

    index = GlobalIndex(
        f"{baseurl}/test-data/input/indexed-urls/global_index.index",
        baseurl=f"{baseurl}/test-data/input/indexed-urls",
    )

    request = dict(param="157")
    retrieve_and_check(index, request)


@pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_per_url_index(baseurl):
    index = PerUrlIndex(
        f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb",
    )
    request = dict(param="157")
    retrieve_and_check(index, request)


def dev():
    baseurl = CML_BASEURL_S3

    index = PerUrlIndex(
        f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb",
    )

    request = dict(param="157")
    retrieve_and_check(index, request)

    request = dict(param="157", time="1000")
    retrieve_and_check(index, request)

    request = dict(date="19970101")
    retrieve_and_check(index, request)

    request = dict(param="157", time="1000", date="19970101")
    retrieve_and_check(index, request)


def timing():
    baseurl = CML_BASEURL_S3
    baseurl = CML_BASEURL_CDS
    index = PerUrlIndex(
        f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb",
    )

    sizes = ["sharp(1,1)", "auto", "cluster"]
    sizes = []
    for r in range(11, 24):  # from 2k to 8M
        sizes.append(f"blocked({2 ** r})")

    report = {}
    for request in [
        dict(param="157"),
        dict(param="157", time="1000"),
        dict(date="19970101"),
        dict(param="157", time="1000", date="19970101"),
    ]:
        times = []
        for n in sizes:
            try:
                elapsed = retrieve_and_check(index, request, range_method=n, force=True)
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


def benchmark():
    collect_statistics(True)

    baseurls = [
        CML_BASEURL_S3,
        CML_BASEURL_CDS,
    ]

    requests = [
        dict(param="157", time=["1100", "1200", "1300", "1400"]),
        dict(param=["157", "129"], time=["0200", "1000", "1800", "2300"]),
        dict(param=["157", "130"], levelist=["500", "850"]),
        dict(param="157", time="1000", date="19970101"),
        dict(param="157", time="1000"),
        dict(param="157"),
        dict(param=["157", "129"]),
        dict(date="19970101"),
    ]

    methods = [
        "sharp(1,1)",
        "cluster(100)",
        "cluster(5)",
        "auto",
        "cluster(5)|debug|blocked(4096)|debug",
        "cluster(1)",
    ]

    for baseurl in baseurls:
        index = PerUrlIndex(
            f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb",
        )
        for request in requests:
            for range_method in methods:
                retrieve_and_check(
                    index,
                    request,
                    range_method,
                    force=True,
                )

    stats = retrieve_statistics()
    import json

    path = "benchmark.json"
    with open(path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"TEST FINISHED. Saved in {path}")


if __name__ == "__main__":
    benchmark()
    # timing()
    # from climetlab.testing import main

    # main(__file__)
