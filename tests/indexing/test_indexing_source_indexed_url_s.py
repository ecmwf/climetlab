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

from climetlab import Dataset, load_source, settings
from climetlab.core.temporary import temp_directory
from climetlab.decorators import normalize
from climetlab.indexing import PerUrlIndex

CML_BASEURL_S3 = "https://storage.ecmwf.europeanweather.cloud/climetlab"
CML_BASEURL_CDS = "https://datastore.copernicus-climate.eu/climetlab"
CML_BASEURL_GET = "https://get.ecmwf.int/repository/test-data/climetlab"
CML_BASEURLS = [CML_BASEURL_S3, CML_BASEURL_GET, CML_BASEURL_CDS]

# Index files have been created with :
#  export BASEURL=https://storage.ecmwf.europeanweather.cloud/climetlab/test-data/input/indexed-urls
#  climetlab index_gribs $BASEURL/large_grib_1.grb > large_grib_1.grb.index
#  climetlab index_gribs $BASEURL/large_grib_2.grb > large_grib_2.grb.index
#  climetlab index_gribs large_grib_1.grb large_grib_2.grb --baseurl $BASEURL > global_index.index


def check(ds, i, ref):
    field = ds[i]
    n = field.to_numpy()
    mean = n.mean()
    assert abs(mean - ref) < 1e-6, (mean, ref, field)


@pytest.mark.long_test
@pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_indexed_s3(baseurl):
    PER_URL_INDEX = PerUrlIndex(
        baseurl + "/test-data/input/indexed-urls/large_grib_{n}.grb"
    )

    class Mydataset(Dataset):
        @normalize(
            "param",
            ["q", "r", "t", "u", "v", "z"],
            # aliases="eumetnet_aliases.yaml",
            # multiple=True,
        )
        def __init__(self, option="abc", **request):
            self.source = load_source(
                "indexed-urls",
                PER_URL_INDEX,
                request,
            )

            self.source = load_source(
                "indexed-urls",
                baseurl + "/test-data/input/indexed-urls/large_grib_{n}.grb",
                request,
            )

    a = Mydataset(
        **{
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
    )
    check(a, 0, 49.86508481081071)
    ds = a.to_xarray()
    assert abs(ds["r"].mean() - 49.86508560180664) < 1e-6


def retrieve_and_check_url(*args, **kwargs):
    load_source(*args, **kwargs)


def retrieve_and_check(index, request, range_method=None, **kwargs):
    print("--------")
    print("range_method", range_method)
    print("REQUEST", request)
    #    for url, p in parts:
    #        total = len(index.get_backend(url).entries)
    #        print(f"PARTS: {len(p)}/{total} parts in {url}")

    now = time.time()
    s = load_source(  # noqa F841
        "indexed-urls",
        index,
        request,
        range_method=range_method,
        **kwargs,
    )
    elapsed = time.time() - now
    # print("ELAPSED", elapsed)
    # try:
    #     paths = [s.path]
    # except AttributeError:
    #     paths = [p.path for p in s.sources]

    # for path in paths:
    #     # check that the downloaded gribs match the request
    #     for grib in load_source("file", path):
    #         for k, v in request.items():
    #             if k == "param":
    #                 k = "shortName"
    #             assert check_grib_value(grib._get(k), v), (grib._get(k), v)
    return elapsed


def check_grib_value(value, requested):
    if isinstance(requested, (list, tuple)):
        return any([check_grib_value(value, _v) for _v in requested])
    else:
        try:
            return int(value) == int(requested)
        except (TypeError, ValueError):
            return str(value) == str(requested)


@pytest.mark.long_test
@pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_global_index(baseurl):
    with temp_directory() as tmpdir:
        with settings.temporary():
            settings.set("cache-directory", tmpdir)

            print(f"{baseurl}/test-data/input/indexed-urls/global_index.index")
            s = load_source(
                "indexed-url",
                f"{baseurl}/test-data/input/indexed-urls/global_index.index",
                # baseurl=f"{baseurl}/test-data/input/indexed-urls",
                param="r",
                time="1000",
                date="19970101",
                index_type="json",
                # db_path='./here.json'
            )
            for _ in s:
                print(_)
                break
            s.to_xarray()

            # for path in paths:
            #     # check that the downloaded gribs match the request
            #     for grib in load_source("file", path):
            #         for k, v in request.items():
            #             if k == "param":
            #                 k = "shortName"
            #             assert check_grib_value(grib._get(k), v), (grib._get(k), v)


@pytest.mark.long_test
@pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_per_url_index(baseurl):
    index = PerUrlIndex(
        f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb",
    )
    request = dict(param="r", time="1000", date="19970101")
    retrieve_and_check(index, request)


@pytest.mark.long_test
# @pytest.mark.parametrize("baseurl", CML_BASEURLS)
def test_per_url_index_2():
    baseurl = CML_BASEURL_S3
    index = PerUrlIndex(
        f"{baseurl}/test-data/big.grib",
    )
    request = dict(param="cin", date="20211125", step="6", number=["1", "3"])
    retrieve_and_check(index, request)


def dev():
    baseurl = CML_BASEURL_S3

    index = PerUrlIndex(
        f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb",
    )

    request = dict(param="r")
    retrieve_and_check(index, request)

    request = dict(param="r", time="1000")
    retrieve_and_check(index, request)

    request = dict(date="19970101")
    retrieve_and_check(index, request)

    request = dict(param="r", time="1000", date="19970101")
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
        dict(param="r"),
        dict(param="r", time="1000"),
        dict(date="19970101"),
        dict(param="r", time="1000", date="19970101"),
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


@pytest.mark.long_test
def test_grib_index_eumetnet():
    request = {
        "param": "2ti",
        "date": "20171228",
        "step": ["0-24", "24-48", "48-72", "72-96", "96-120", "120-144", "144-168"],
        # Parameters passed to the filename mangling
        "url": "https://storage.ecmwf.europeanweather.cloud/eumetnet-postprocessing-benchmark-training-dataset/",
        "month": "12",
        "year": "2017",
    }
    PATTERN = "{url}data/fcs/efi/" "EU_forecast_efi_params_{year}-{month}_0.grb"
    ds = load_source("indexed-urls", PerUrlIndex(PATTERN), request)
    assert len(ds) == 7, len(ds)
    check(ds, 0, -0.16334878510300832)
    check(ds, 1, -0.06413754859021915)
    check(ds, 2, 0.23404628380396034)
    check(ds, 3, 0.3207112379535552)
    xds = ds.to_xarray()
    print(xds)


if __name__ == "__main__":
    # test_per_url_index(CML_BASEURL_CDS)
    test_indexed_s3(CML_BASEURL_S3)
    # timing()
    # from climetlab.testing import main

    # main(__file__)
    # test_grib_index_eumetnet()
