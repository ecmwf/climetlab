# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import time

from climetlab import load_source
from climetlab.core.statistics import collect_statistics, retrieve_statistics
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
    print("REQUEST", request, index)
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


def plot(df):
    import matplotlib.pyplot as plt
    import seaborn as sns

    for k in ["url", "parts", "blocks"]:
        if k in df:
            del df[k]

    x = "nparts"

    df = df.sort_values(by=[x])
    # g = sns.FacetGrid(data=df, col="method", hue='server', height=3, aspect=1.5, col_wrap=3)
    g = sns.FacetGrid(
        data=df, col="server", hue="method", height=4, aspect=1.5, col_wrap=3
    )
    g = g.map(plt.semilogx, x, "speed")  # , shade=True)
    g.add_legend()

    # print(f"BENCHMARK FINISHED. Panda saved in {path}")


def radix(long, sep="("):
    assert long is not None, long
    if not isinstance(long, str):
        return long
    if sep not in long:
        return long
    return long.split(sep)[0]


def url_to_server(url):
    if url.startswith(CML_BASEURL_S3):
        return "EWC"
    if url.startswith(CML_BASEURL_CDS):
        return "CDS"
    if url.startswith(CML_BASEURL_GET):
        return "GET"
    return "Other"


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
        dict(
            param=["r", "z"],
            time=["0200", "1000", "1800", "2300"],
            levelist=["500", "850"],
        ),
        dict(
            param=["r", "z", "t"],
            time=["0200", "1000", "1800", "2300"],
            levelist=["500", "850"],
        ),
        dict(
            param=["t"], time=["0200", "1000", "1800", "2300"], levelist=["500", "850"]
        ),
        dict(param=["r", "t"], levelist=["500", "850"]),
        dict(param="r", time="1000", date="19970101"),
        dict(param="r", time="1000"),
        dict(param="r"),
        dict(param=["r", "z"]),
        dict(date="19970101"),
    ]

    methods = []
    for i in [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100]:
        methods.append(f"sharp({i},1)")

    for i in [1, 5, 10, 50, 100, 500, 1000]:
        methods.append(f"cluster({i})")

    methods.append("auto")

    for i in range(12, 25, 2):
        methods.append(f"blocked({2**i})")

    methods.append("cluster(5)|blocked(4096)")

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

    run_id = get_run_id()

    path = f"climetlab_benchmark{run_id}.json"
    stats.write_to_json(path)
    stats.write_to_json("climetlab_benchmark.json")

    df = stats.to_pandas()

    df.to_csv(f"climetlab_benchmark.raw{run_id}.csv")

    print(f"BENCHMARK FINISHED. Logs saved in {path}")

    df["server"] = df["url"].apply(url_to_server)
    df["speed"] = df["total"] / df["elapsed"] / (1024 * 1024)  # MB/s

    df["method"] = df["full_method"].apply(radix)

    df.to_csv(f"climetlab_benchmark{run_id}.csv")
    df.to_csv("climetlab_benchmark.csv")

    plot(df)


def get_run_id(keys=("hostname", "ip", "date", "user", "time")):
    run_id = ""

    import datetime

    now = datetime.datetime.now()

    for k in keys:
        if k == "hostname":
            import socket

            run_id += "_" + str(socket.gethostname())
            continue

        if k == "user":
            import getpass

            run_id += "_" + str(getpass.getuser())
            continue

        if k == "ip":
            from requests import get

            ip = get("https://api.ipify.org").text
            run_id += "_" + str(ip)

        if k == "date":
            run_id += "_" + now.strftime("%Y-%m-%d")

        if k == "time":
            run_id += "_" + now.strftime("%H:%M")

    return run_id
