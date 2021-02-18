#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.utils.dates import to_datetimes_list, to_datetime
import numpy as np
import datetime
from climetlab import load_source


def test_to_datetime():
    pydate = datetime.datetime(2016, 1, 1)

    assert to_datetime(np.datetime64("2016-01-01")) == pydate

    assert to_datetime(np.datetime64("2016-01-01 00:00:00")) == pydate

    assert to_datetime(datetime.date(2016, 1, 1)) == pydate

    assert to_datetime("2016-01-01") == pydate

    assert to_datetime("2016-01-01T00:00:00") == pydate


def test_to_datetimes_list_grib():
    source = load_source("file", "docs/examples/test.grib")
    for s in source:
        assert to_datetimes_list(s) == [datetime.datetime(2020, 5, 13, 12, 0)]


if __name__ == "__main__":
    # test_to_datetime()
    to_datetimes_list()
