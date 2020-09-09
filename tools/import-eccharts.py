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

import yaml

SOURCE = os.path.expanduser("~/git/webdev/data/catalogue/eccharts/projection")
TARGET = os.path.expanduser("~/git/climetlab/climetlab/data/projections")

M = {
    "lower_left_latitude": "subpage_lower_left_latitude",
    "lower_left_longitude": "subpage_lower_left_longitude",
    "projection": "subpage_map_projection",
    "upper_right_latitude": "subpage_upper_right_latitude",
    "upper_right_longitude": "subpage_upper_right_longitude",
    "map_hemisphere": "subpage_map_hemisphere",
    "vertical_longitude": "subpage_vertical_longitude",
}


for root, _, files in os.walk(SOURCE):
    for file in files:
        if file.endswith(".json"):
            path = os.path.join(root, file)
            print(path)
            if "countr" in path:
                continue
            with open(path) as f:
                x = json.loads(f.read())
                name = os.path.basename(path)[:-5].replace("_", "-")
                if x.get("enabled", False) and x.get("in_production", False):
                    data = x["data"]
                    for k in list(data.keys()):
                        data[M[k]] = data.pop(k)

                    data = dict(magics=dict(mmap=data))

                    print(name)
                    with open(os.path.join(TARGET, name + ".yaml"), "w") as f:
                        yaml.dump(data, f, default_flow_style=False)
