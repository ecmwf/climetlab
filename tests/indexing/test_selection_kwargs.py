#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import datetime

import pytest

import climetlab as cml
from climetlab.core.select import normalize_selection

to_kwargs = normalize_selection


def test_selection_1():
    ref = dict(date=[1, 2, 3], time=None, param="abc", number=3.0, lst=["xyz"])

    assert to_kwargs(ref) == ref


def test_selection_with_all():
    ref = dict(date=all, time=7, step=[6])

    assert to_kwargs(ref) == ref
    assert to_kwargs(date=all, time=7, step=[6]) == ref
    assert to_kwargs(date=cml.ALL, time=7, step=[6]) == ref


def test_selection_with_date_1():
    ref = dict(date="2008-07-19", step=5)

    assert to_kwargs(ref) == ref
    assert to_kwargs(date="2008-07-19", step=5) == ref
    # assert to_kwargs(date=datetime.datetime(2008,7,19), step=5) == ref


def test_selection_with_date_3():
    ref = dict(date=datetime.datetime(2008, 7, 19), step=5)

    assert to_kwargs(ref) == ref


def test_selection_with_date_4():
    ref = dict(
        date=[datetime.datetime(2008, 7, 19), datetime.datetime(2008, 7, 20)],
        step=5,
    )

    assert to_kwargs(ref) == ref


def test_selection_with_none():
    ref = dict(param="p", time=None)

    assert to_kwargs(ref) == ref
    assert to_kwargs(param="p", time=None) == ref


def test_selection_must_fail():
    with pytest.raises(ValueError):
        assert to_kwargs("date", "time")
    with pytest.raises(ValueError):
        assert to_kwargs(["date", "time"])
    with pytest.raises(ValueError):
        assert to_kwargs([dict(date="2008-07-19", step=5)])


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
