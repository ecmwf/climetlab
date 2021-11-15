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
import os
import time
from collections import defaultdict

from climetlab import load_source

BASEURL = "https://storage.ecmwf.europeanweather.cloud/benchmark-dataset"

# wget-recursive  "https://storage.ecmwf.europeanweather.cloud/benchmark-dataset"
# climetlab index_gribs data > EU.index

# path = "data/ana/pressure/EU_analysis_pressure_params_1997-01.grb"


class UrlsParts:
    def __init__(self):
        self.parts = defaultdict(list)

    def append(self, e):
        path = e["_path"]
        offset = e["_offset"]
        length = e["_length"]

        self.parts[path].append((offset, length))

    def __repr__(self):
        n = sum(len(x) for x in self.parts.values())
        return f"{len(self.parts)} HTTP requests with a total of {n} parts"

    def to_source(self, baseurl, **kwargs):
        sources = []
        for path, ranges in self.parts.items():
            source = load_source(
                "url",
                url=f"{baseurl}/{path}",
                parts=sorted(ranges),
                lazily=True,
                **kwargs,
            )
            sources.append(source)
        if not sources:
            raise ValueError("Empty request: no match.")
        return load_source("multi", *sources)


class GribIndex:
    def __init__(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
        self.entries = []
        for line in lines:
            entry = json.loads(line)
            self.entries.append(entry)

    def match(self, entry, request):
        for k, v in request.items():
            if entry[k] != v:
                return False
        return True

    def request_to_url_parts(self, request):
        parts = UrlsParts()
        for e in self.entries:
            if self.match(e, request):
                parts.append(e)
        print(f"Build HTTP requests for {request}: {parts} ")
        return parts


def retrieve_and_check(index, request, **kwargs):
    parts = index.request_to_url_parts(request)
    print("REQUEST", request)
    print("PARTS", parts)

    now = time.time()
    s = parts.to_source(baseurl=BASEURL, **kwargs)
    elapsed = time.time() - now
    print("ELAPSED", elapsed)
    try:
        paths = [s.path]
    except AttributeError:
        paths = [p.path for p in s.sources]

    for path in paths:
        for grib in load_source("file", path):
            for k, v in request.items():
                assert str(grib._get(k)) == str(v), (grib._get(k), v)
    return elapsed


def dev():
    index = GribIndex(os.path.join(os.path.dirname(__file__), "EU.index"))

    request = dict(param="157.128")
    retrieve_and_check(index, request)

    request = dict(param="157.128", time="1000")
    retrieve_and_check(index, request)

    request = dict(date="19970101")
    retrieve_and_check(index, request)

    request = dict(param="157.128", time="1000", date="19970101")
    retrieve_and_check(index, request)


def timing():
    index = GribIndex(os.path.join(os.path.dirname(__file__), "EU.index"))

    sizes = [None, "auto"]
    n = 8 * 1024 * 1024
    while n > 1024:
        sizes.append(n)
        n //= 2

    report = {}
    for request in [
        dict(param="157.128"),
        dict(param="157.128", time="1000"),
        dict(date="19970101"),
        dict(param="157.128", time="1000", date="19970101"),
    ]:
        times = []
        for n in sizes:
            elapsed = retrieve_and_check(index, request, transfer_size=n, force=True)
            if n is None:
                n = 0
            if n == "auto":
                n = -1
            times.append((round(elapsed * 10) / 10.0, n))

        report[tuple(request.items())] = request, sorted(times)

    for k, v in report.items():
        print(k)
        print(v)


if __name__ == "__main__":
    dev()
    # from climetlab.testing import main

    # main(__file__)
