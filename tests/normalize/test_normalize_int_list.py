#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.decorators import normalize


def x_no_default(x):
    return x


def test_int_list_normalizers():
    g = x_no_default
    g = normalize("x", "int-list")(g)
    assert g(x=1) == [1]
    assert g(x=(1, 2)) == [1, 2]
    assert g(x=("1", 2)) == [1, 2]
    assert g(x="1") == [1]
    assert g(x="1/to/3") == [1, 2, 3]
    assert g(x="1/to/3/by/2") == [1, 3]


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
