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
from collections import defaultdict

import climetlab
from climetlab.sources.multi import MultiSource

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
        n = 0
        return f"{len(self.parts)} HTTP requests with {n} parts"

    def to_source(self, baseurl):
        sources = []
        for path, ranges in self.parts.items():
            source = climetlab.load_source(
                "url",
                url=f"{baseurl}/{path}",
                parts=sorted(ranges),
            )
            print(source)
            sources.append(source)
        if not sources:
            raise ValueError("Empty request: no match.")
        s = MultiSource(*sources)
        return s


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


def dev():
    index = GribIndex(os.path.join(os.path.dirname(__file__), "EU.index"))

    # request = dict(param="157.128")
    request = dict(param="157.128", time="1000")
    # request = dict(date="19970101")
    # request = dict(param="157.128", time="1000", date="19970101")

    parts = index.request_to_url_parts(request)

    s = parts.to_source(baseurl=BASEURL)
    print(s)
    print(s.to_xarray())


if __name__ == "__main__":
    dev()
    # from climetlab.testing import main

    # main(__file__)
