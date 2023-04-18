#!/usr/bin/env python3

# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import pytest

from climetlab.core.order import normalize_order_by

to_kwargs = normalize_order_by


def test_order_1():
    ref = {"date": "ascending", "time": "ascending", "level": "ascending"}

    assert to_kwargs(ref) == ref

    assert to_kwargs("date", "time", "level") == ref
    assert to_kwargs(["date", "time", "level"]) == ref
    assert to_kwargs(("date", "time", "level")) == ref


def test_order_2():
    ref = {"date": "descending", "time": "ascending", "level": "ascending"}

    assert to_kwargs(ref) == ref
    assert to_kwargs(dict(date="descending"), "time", "level") == ref
    assert to_kwargs(dict(date="descending"), ["time", "level"]) == ref


def test_order_3():
    ref = {"date": "ascending", "time": "ascending", "level": "descending"}

    assert to_kwargs(ref) == ref
    assert to_kwargs("time", "date", dict(level="descending")) == ref


def test_order_4():
    ref = {"date": None, "time": "ascending", "level": None}
    assert to_kwargs(dict(date=None), "time", dict(level=None)) == ref


def test_order_must_fail():
    with pytest.raises(ValueError):
        assert to_kwargs(5, 4)
    with pytest.raises(ValueError):
        assert to_kwargs([4, 5])
    with pytest.raises(ValueError):
        assert to_kwargs(a="ascending", b="blah")


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
