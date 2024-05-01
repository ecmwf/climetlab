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
import logging
import os

import pytest

from climetlab import load_source
from climetlab import settings
from climetlab.core.caching import cache_entries
from climetlab.core.caching import cache_file
from climetlab.core.caching import cache_size
from climetlab.core.caching import dump_cache_database
from climetlab.core.caching import purge_cache
from climetlab.core.temporary import temp_directory
from climetlab.testing import TEST_DATA_URL

LOG = logging.getLogger(__name__)


def test_cache_1():
    purge_cache(matcher=lambda e: ["owner"] == "test_cache")

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


# @pytest.mark.skipif(True, reason="Test fails in github, needs fixing")
@pytest.mark.download
def test_cache_2():
    with temp_directory() as tmpdir:
        with settings.temporary():
            settings.set("cache-directory", tmpdir)
            settings.set("maximum-cache-size", "5MB")
            settings.set("number-of-download-threads", 5)

            assert cache_size() == 0

            load_source(
                "url-pattern",
                f"{TEST_DATA_URL}/input/" + "1mb-{n}.bin",
                {
                    "n": [0, 1, 2, 3, 4],
                },
            )

            cachesize = cache_size()
            expected = 5 * 1024 * 1024
            if cachesize != expected:
                print(json.dumps(dump_cache_database(), indent=4))
                assert cachesize == expected, ("before", cachesize / 1024.0 / 1024.0)

            cnt = 0
            for i, f in enumerate(cache_entries()):
                # print("FILE", i, f)
                cnt += 1
            if cnt != 5:
                print(json.dumps(dump_cache_database(), indent=4))
                assert cnt == 5, f"Files in cache database (before): {cnt}"

            load_source(
                "url-pattern",
                f"{TEST_DATA_URL}/input/" + "1mb-{n}.bin",
                {
                    "n": [5, 6, 7, 8, 9],
                },
            )

            cachesize = cache_size()
            expected = 5 * 1024 * 1024
            if cachesize != expected:
                print(json.dumps(dump_cache_database(), indent=4))
                assert cachesize == expected, ("after", cachesize / 1024.0 / 1024.0)

            cnt = 0
            for i, f in enumerate(cache_entries()):
                LOG.debug("FILE %s %s", i, f)
                cnt += 1
            if cnt != 5:
                print(json.dumps(dump_cache_database(), indent=4))
                assert cnt == 5, f"Files in cache database (after): {cnt}"

            cnt = 0
            for n in os.listdir(tmpdir):
                if n.startswith("cache-") and n.endswith(".db"):
                    continue
                cnt += 1
            if cnt != 5:
                print(json.dumps(dump_cache_database(), indent=4))
                assert cnt == 5, f"Files in cache directory: {cnt}"


# 1GB ram disk on MacOS (blocks of 512 bytes)
# diskutil erasevolume HFS+ "RAMDisk" `hdiutil attach -nomount ram://2097152`
@pytest.mark.skipif(not os.path.exists("/Volumes/RAMDisk"), reason="No RAM disk")
def test_cache_4():
    with settings.temporary():
        settings.set("cache-directory", "/Volumes/RAMDisk/climetlab")
        settings.set("maximum-cache-disk-usage", "90%")
        for n in range(10):
            load_source("climetlab-testing", "zeros", size=100 * 1024 * 1024, n=n)


@pytest.mark.skip("Not implemented yet")
def test_multiprocessing():
    import multiprocessing

    import climetlab as cml

    def func(val):
        # import climetlab as cml
        source = cml.load_source("url", "https://github.com/ecmwf/climetlab/raw/main/docs/examples/test.grib")
        source.to_xarray()
        return val + 1

    func(0)

    procs = 2
    pool = multiprocessing.Pool(processes=procs)
    for res in pool.imap(func, range(4)):
        print(f"Processed val: {res}")


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
