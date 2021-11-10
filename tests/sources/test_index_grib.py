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

import climetlab
from climetlab.sources.multi import MultiSource

BASEURL = "https://storage.ecmwf.europeanweather.cloud/benchmark-dataset"

# wget-recursive  "https://storage.ecmwf.europeanweather.cloud/benchmark-dataset"
# climetlab index_gribs data > EU.index

# path = "data/ana/pressure/EU_analysis_pressure_params_1997-01.grb"


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
        url_parts = []
        for e in self.entries:
            if self.match(e, request):
                url_parts.append(
                    dict(path=e["_path"], offset=e["_offset"], length=e["_length"])
                )
        print(f"{len(url_parts)} HTTP requests for {request}")
        return url_parts

    def parts_to_source(self, baseurl, parts):
        sources = []
        for part in parts:
            source = climetlab.load_source(
                "url",
                url=f"{baseurl}/{part['path']}",
                offsets=[part["offset"]],
                lengths=[part["length"]],
            )
            sources.append(source)
        if not sources:
            raise ValueError("Empty request: no match.")
        s = MultiSource(*sources)
        return s


def dev():
    index = GribIndex("EU.index")

    # request = dict(param="157.128")
    request = dict(param="157.128", time="1000")

    parts = index.request_to_url_parts(request)

    s = index.parts_to_source(baseurl=BASEURL, parts=parts)
    print(s.to_xarray())


if __name__ == "__main__":
    dev()
    # from climetlab.testing import main

    # main(__file__)
