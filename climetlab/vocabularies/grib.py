# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json

from climetlab.utils import download_and_cache

URL = "https://apps.ecmwf.int/codes/grib/json/"

PARAMS = {}


def _param_id_dict():
    if not PARAMS:
        path = download_and_cache(URL)
        with open(path) as f:
            entries = json.load(f)

        for entry in entries["parameters"]:
            PARAMS[int(entry["param_id"])] = entry

    return PARAMS


def param_id_to_dict(param_id):
    dic = _param_id_dict()
    return dic[param_id]


def param_id_to_short_name(param_id):
    entry = param_id_to_dict(param_id)
    return entry["param_shortName"]


if __name__ == "__main__":

    import sys

    for i in sys.argv[1:]:
        print(param_id_to_short_name(int(i)))
