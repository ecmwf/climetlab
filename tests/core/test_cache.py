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

import pytest

from climetlab import load_source, settings
from climetlab.core.caching import cache_entries, cache_file, cache_size, purge_cache
from climetlab.core.temporary import temp_directory


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
    for f in cache_entries():
        if f["owner"] == "test_cache":
            cnt += 1

    assert cnt == 2


def test_cache_2():

    with temp_directory() as tmpdir:
        with settings.temporary():
            settings.set("cache-directory", tmpdir)
            settings.set("maximum-cache-size", "5MB")
            settings.set("number-of-download-threads", 5)

            assert cache_size() == 0

            load_source(
                "url-pattern",
                "https://get.ecmwf.int/test-data/climetlab/1mb-{n}.bin",
                {
                    "n": [0, 1, 2, 3, 4],
                },
            )

            assert cache_size() == 5 * 1024 * 1024, cache_size()

            cnt = 0
            for i, f in enumerate(cache_entries()):
                print("FILE", i, f)
                cnt += 1
            assert cnt == 5, f"Files in cache database: {cnt}"

            load_source(
                "url-pattern",
                "https://get.ecmwf.int/test-data/climetlab/1mb-{n}.bin",
                {
                    "n": [5, 6, 7, 8, 9],
                },
            )

            assert cache_size() == 5 * 1024 * 1024, cache_size() / 1024.0 / 1024.0

            cnt = 0
            for i, f in enumerate(cache_entries()):
                print("FILE", i, f)
                cnt += 1
            assert cnt == 5, f"Files in cache database: {cnt}"

            cnt = 0
            for n in os.listdir(tmpdir):
                if n.startswith("cache-") and n.endswith(".db"):
                    continue
                cnt += 1
            assert cnt == 5, f"Files in cache directory: {cnt}"


# 1GB ram disk on MacOS (blocks of 512 bytes)
# diskutil erasevolume HFS+ "RAMDisk" `hdiutil attach -nomount ram://2097152`
@pytest.mark.skipif(not os.path.exists("/Volumes/RAMDisk"), reason="No RAM disk")
def test_cache_4():
    with settings.temporary():
        settings.set("cache-directory", "/Volumes/RAMDisk/climetlab")
        settings.set("maximum-cache-disk-usage", "90%")
        for n in range(10):
            load_source("dummy-source", "zeros", size=100 * 1024 * 1024, n=n)


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
