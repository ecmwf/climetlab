#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import time

import climetlab as cml
from climetlab.utils import download_and_cache

from utils import data_file


def test_download():
    url = (
        "https://github.com/ecmwf/climetlab/raw/master/docs/examples/test.grib?_=%s"
        % (time.time(),)
    )
    download_and_cache(url)

def test_local():
    ds = cml.load_source('url','file://{}'.format(data_file('single/z_500_20000101.grib'),))
    assert len(ds) == 1

def test_ftp():
    pass

# TODO: test .tar, .zip, .tar.gz
if __name__ == "__main__":
    for k, f in sorted(globals().items()):
        if k.startswith("test_") and callable(f):
            print(k)
            f()
