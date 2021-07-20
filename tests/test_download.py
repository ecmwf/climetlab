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
import pathlib
import time

from climetlab import settings
from climetlab.utils import download_and_cache


def path_to_url(path):
    return pathlib.Path(os.path.abspath(path)).as_uri()


def test_download_1():
    url = "https://github.com/ecmwf/climetlab/raw/main/docs/examples/test.grib?_=%s" % (
        time.time(),
    )
    download_and_cache(url)


def test_download_2():
    url = "https://github.com/ecmwf/climetlab/raw/main/docs/examples/test.grib"
    download_and_cache(url)


def test_download_3():
    with settings.temporary("download-updated-urls", True):
        url = "https://get.ecmwf.int/test-data/climetlab/test.txt"
        download_and_cache(url)


def test_download_4():
    url = "https://get.ecmwf.int/test-data/climetlab/missing.txt"
    r = download_and_cache(url, return_none_on_404=True)
    assert r is None, r


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
