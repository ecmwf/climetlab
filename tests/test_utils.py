#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.utils import bytes_to_string


def test_bytes():
    assert bytes_to_string(10) == "10"
    assert bytes_to_string(1024) == "1 KiB"
    assert bytes_to_string(1024*1024) == "1 MiB"
