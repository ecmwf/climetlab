#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.utils.datetime import datetimes_to_dates_and_times


def test_dates():
    assert datetimes_to_dates_and_times("1/3/99", as_request=True) == [
        (("1999-01-03",), ("00:00",))
    ]
