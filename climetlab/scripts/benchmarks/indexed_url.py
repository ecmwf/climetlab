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

CML_BASEURL_S3 = "https://storage.ecmwf.europeanweather.cloud/climetlab"
CML_BASEURL_CDS = "https://datastore.copernicus-climate.eu/climetlab"
CML_BASEURL_GET = "https://get.ecmwf.int/repository/test-data/climetlab"


def get_methods_list():
    methods = []
    # methods.append("cluster(2)|blocked(256)")
    # methods.append("cluster(5)|blocked(4096)")
    for i in [10, 100]:
        for j in [12, 16, 24]:
            methods.append(f"cluster({i})|blocked({2**j})")

    # for i in range(1,10,2):
    #     methods.append(f"sharp({10**i},1)")

    # for i in [1, 2, 3, 4, 5, 7, 10, 20, 50, 100, 500, 1000]:
    for i in [1, 5, 10, 50, 100]:
        methods.append(f"cluster({i})")

    methods.append("auto")

    for i in range(8, 25, 4):
        methods.append(f"blocked({2**i})")

    return methods


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
    parts = index.get_path_offset_length(request)
    print("range_method", range_method)
    print("REQUEST", request)
    for url, p in parts:
        total = len(index.get_backend(url).entries)
        print(f"PARTS: {len(p)}/{total} parts in {url}")

    ####################
    # from climetlab import load_source
    # from climetlab.indexing import PerUrlIndex
    #
    # baseurl = "https://datastore.copernicus-climate.eu/climetlab"
    # s = load_source(
    #     "indexed-urls",
    #     PerUrlIndex(
    #         f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb",
    #     ),
    #     {"param": "r", "time": "1200"},
    #     range_method="auto",
    #     force=True,
    # )
    # assert 0, "Stop here"
    ####################

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
        CML_BASEURL_CDS,
        # CML_BASEURL_GET,
    ]

    requests = [
        {"param": "r", "time": "1000", "step": "0"},
        {"param": "r", "time": "1000"},
        {"param": "r", "time": ["1100", "1200", "1300", "1400"]},
        {
            "param": ["r", "z"],
            "time": ["0200", "1000", "1800", "2300"],
            "levelist": ["500", "850"],
        },
        {"param": ["r", "z"], "levelist": ["500", "850"]},
        {"param": "r"},
        # {"param": ["r", "z"]},
        {"param": ["r", "z", "t"]},
        # {},
    ]

    methods = get_methods_list()

    # requests = [requests[2]]
    # methods = [methods[0]]
    # baseurls = [baseurls[0]]
    # requests = requests[::2]
    # methods = methods[::2]
    # baseurls = [baseurls[0]]
    failed = []
    successfull = 0
    import tqdm

    from climetlab.indexing import PerUrlIndex

    for request in tqdm.tqdm(requests):
        for range_method in tqdm.tqdm(methods):
            for baseurl in baseurls:
                index = PerUrlIndex(
                    f"{baseurl}/test-data/input/indexed-urls/large_grib_1.grb",
                )
                try:
                    retrieve_and_check(
                        index,
                        request,
                        range_method,
                        force=True,
                    )
                    successfull += 1
                except Exception as e:
                    failed.append((index, request, range_method))
                    print("FAILED for ", index, request, range_method)
                    print(e)

    stats = retrieve_statistics()

    run_id = get_run_id()

    logfiles = []

    path = f"climetlab_benchmark{run_id}.json"
    logfiles.append(path)
    stats.write_to_json(path)
    print(f"BENCHMARK FINISHED. Raw logs saved in {path}")

    df = stats.to_pandas()

    df["server"] = df["url"].apply(url_to_server)
    df["speed"] = df["total"] / df["elapsed"] / (1024 * 1024)  # MB/s
    df["method"] = df["full_method"].apply(radix)

    df = df.rename(
        dict(
            size_parts="size_requested",
            size_blocks="size_downloaded",
        )
    )
    df["size_ratio"] = df["size_downloaded"] / df["size_requested"]

    path = f"climetlab_benchmark{run_id}.csv"
    df.to_csv(path)
    # df.to_csv("climetlab_benchmark.csv")
    logfiles.append(path)

    print(f"Benchmark finished ({successfull} successfull, {len(failed)} failed).")
    print(
        "All data in the log files are anonymous."
        "Only the log file names contain personal data (machine name, IP, etc.)."
    )
    for f in logfiles:
        print(f"Log file: {f}")


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
            run_id += "_" + now.strftime("%H%M")

    return run_id
