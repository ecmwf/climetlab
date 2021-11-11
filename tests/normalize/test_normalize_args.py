#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from climetlab.normalize import normalize_args


def a_b_no_default(a, b):
    return a, b


def test_normalize_args():
    @normalize_args(
        dates="date-list(%Y.%m.%d)",
        names=["a", "b", "c"],
        name=("A", "B", "C"),
    )
    def f(dates, names, name):
        return dates, names, name

    assert f("20200101", "A", "b") == (["2020.01.01"], ["a"], "B")


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
