#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

from climetlab.core.caching import cache_file, get_cached_files, purge_cache


def test_cache():

    purge_cache(owner="test_cache")

    path1 = cache_file("test_cache", {"foo": 1}, extension=".test")
    path2 = cache_file("test_cache", {"foo": 2}, extension=".test")

    assert not os.path.exists(path1), f"Path already exists: {path1}"
    assert not os.path.exists(path2), f"Path already exists: {path2}"
    assert path1 != path2, f"{path1} == {path2}"

    cnt = 0
    for f in get_cached_files():
        if f["owner"] == "test_cache":
            cnt += 1

    assert cnt == 2


if __name__ == "__main__":
    test_cache()
