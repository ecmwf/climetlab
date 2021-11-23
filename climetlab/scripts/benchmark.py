# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import json
import time

from climetlab import load_source
from climetlab.core.statistics import (
    collect_statistics,
    retrieve_statistics,
    stats_to_pandas,
)
from climetlab.indexing import PerUrlIndex

CML_BASEURL_S3 = "https://storage.ecmwf.europeanweather.cloud/climetlab"
CML_BASEURL_CDS = "https://datastore.copernicus-climate.eu/climetlab"
CML_BASEURL_GET = "https://get.ecmwf.int/repository/test-data/climetlab"


def check_grib_value(value, requested):
    if isinstance(requested, (list, tuple)):
        return any([check_grib_value(value, _v) for _v in requested])
    else:
        try:
            return int(value) == int(requested)
        except (TypeError, ValueError):
            return str(value) == str(requested)


def retrieve_and_check(index, request, range_method=None, **kwargs):
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
                if k == "param":
                    k = "shortName"
                assert check_grib_value(grib._get(k), v), (grib._get(k), v)
    return elapsed


def benchmark():
    collect_statistics(True)

    baseurls = [
        CML_BASEURL_S3,
        # CML_BASEURL_CDS,
        CML_BASEURL_GET,
    ]

    requests = [
        dict(param="r", time=["1100", "1200", "1300", "1400"]),
        dict(param=["r", "z"], time=["0200", "1000", "1800", "2300"]),
        dict(param=["r", "t"], levelist=["500", "850"]),
        dict(param="r", time="1000", date="19970101"),
        dict(param="r", time="1000"),
        dict(param="r"),
        dict(param=["r", "z"]),
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

    for request in requests:
        for range_method in methods:
            for baseurl in baseurls:
                index = PerUrlIndex(
                    f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb",
                )
                retrieve_and_check(
                    index,
                    request,
                    range_method,
                    force=True,
                )

    stats = retrieve_statistics()
    keys = ("indexed-urls", "parts-heuristics", "byte-ranges", "transfer")

    path = "benchmark.json"
    with open(path, "w") as f:
        json.dump(stats, f, indent=2)

    df = stats_to_pandas(stats, keys)

    print(f"BENCHMARK FINISHED. JSON log saved in {path}")

    df["server"] = df["url"].apply(lambda url: url_to_server(url))
    df["nparts"] = df["parts"].apply(lambda x: len(x))
    df["nblocks"] = df["blocks"].apply(lambda x: len(x))
    df["speed"] = df["total"] / df["elapsed"] / (1024 * 1024)  # MB/s
    for k in ["url", "parts", "blocks"]:
        if k in df:
            del df[k]

    plot(df)


def plot(df):
    import matplotlib.pyplot as plt
    import seaborn as sns

    x = "nblocks"
    x = "nparts"

    df = df.sort_values(by=[x])
    # g = sns.FacetGrid(data=df, col="method", hue='server', height=3, aspect=1.5, col_wrap=3)
    g = sns.FacetGrid(
        data=df, col="server", hue="method", height=4, aspect=1.5, col_wrap=3
    )
    g = g.map(plt.semilogx, x, "speed")  # , shade=True)
    g.add_legend()

    # print(f"BENCHMARK FINISHED. Panda saved in {path}")


def url_to_server(url):
    if url.startswith(CML_BASEURL_S3):
        return "EWC"
    if url.startswith(CML_BASEURL_CDS):
        return "CDS"
    if url.startswith(CML_BASEURL_GET):
        return "GET"
    return "Other"


class BenchmarkCmd:
    def do_benchmark(self, args):
        print("Started benchmark.")
        benchmark()
