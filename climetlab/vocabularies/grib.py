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


def grib_database():
    path = download_and_cache(URL)
    with open(path) as f:
        entries = json.load(f)

    for entry in entries["parameters"]:
        yield entry


if __name__ == "__main__":

    for n in grib_database():
        print(n)
