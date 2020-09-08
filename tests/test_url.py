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

from climetlab.utils import download_and_cache


def test_download():
    url = (
        "https://github.com/ecmwf/climetlab/raw/master/docs/examples/test.grib?_=%s"
        % (time.time(),)
    )
    download_and_cache(url)


# TODO: test .tar, .zip, .tar.gz
