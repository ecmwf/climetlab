#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import getpass
import os
import shutil
import tempfile

from climetlab import load_source, settings
from climetlab.core.caching import cache_file, cache_size, get_cached_files, purge_cache


def test_cache_1():

    purge_cache(owner="test_cache")

    def touch(target, args):
        assert args["foo"] in (1, 2)
        with open(target, "w"):
            pass

    path1 = cache_file(
        "test_cache",
        touch,
        {"foo": 1},
        extension=".test",
    )

    path2 = cache_file(
        "test_cache",
        touch,
        {"foo": 2},
        extension=".test",
    )

    assert path1 != path2

    cnt = 0
    for f in get_cached_files():
        if f["owner"] == "test_cache":
            cnt += 1

    assert cnt == 2


def test_cache_2():
    directory = os.path.join(
        tempfile.gettempdir(),
        "climetlab-%s-testing" % (getpass.getuser(),),
    )

    if os.path.exists(directory):
        shutil.rmtree(directory)

    try:
        with settings.temporary():
            settings.set("cache-directory", directory)
            settings.set("maximum-cache-size", "5MB")
            settings.set("number-of-download-threads", 5)

            assert cache_size() == 0

            load_source(
                "url-pattern",
                "https://storage.ecmwf.europeanweather.cloud/climetlab/test-data/0.5/cache.{n}.{size}mb",
                {
                    "size": 1,
                    "n": [0, 1, 2, 3, 4],
                },
            )

            assert cache_size() == 5 * 1024 * 1024, cache_size()

            cnt = 0
            for f in get_cached_files():
                print(f)
                cnt += 1
            assert cnt == 5, f"Files in cache database: {cnt}"

            load_source(
                "url-pattern",
                "https://storage.ecmwf.europeanweather.cloud/climetlab/test-data/0.5/cache.{n}.{size}mb",
                {
                    "size": 1,
                    "n": [5, 6, 7, 8, 9],
                },
            )

            assert cache_size() == 5 * 1024 * 1024, cache_size()

            cnt = 0
            for f in get_cached_files():
                cnt += 1
            assert cnt == 5, f"Files in cache database: {cnt}"

            cnt = 0
            for n in os.listdir(directory):
                if n.startswith("cache-") and n.endswith(".db"):
                    continue
                cnt += 1
            assert cnt == 5, f"Files in cache directory: {cnt}"

    finally:
        shutil.rmtree(directory)


if __name__ == "__main__":
    for k, f in sorted(globals().items()):
        if k.startswith("test_") and callable(f):
            print(k)
            f()
