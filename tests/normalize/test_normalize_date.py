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

from climetlab import load_source
from climetlab.decorators import normalize
from climetlab.testing import climetlab_file


def f(d):
    return d


def test_normalize_dates_from_source():

    dates_3 = normalize("d", "date")(f)
    dates_list_3 = normalize("d", "date", multiple=True)(f)

    source = load_source("file", climetlab_file("docs/examples/test.grib"))
    assert dates_3(source[0]) == datetime.datetime(2020, 5, 13, 12, 0)
    assert dates_list_3(source[0]) == [datetime.datetime(2020, 5, 13, 12, 0)]

    source = load_source("file", climetlab_file("docs/examples/test.nc"))

    #  For now
    with pytest.raises(NotImplementedError):
        assert dates_3(source[0]) == datetime.datetime(2020, 5, 13, 12, 0)
        assert dates_list_3(source[0]) == [datetime.datetime(2020, 5, 13, 12, 0)]


def test_dates_formated_1():
    date_formated = normalize("d", "date", format="%Y.%m.%d")(f)

    assert date_formated("20200513") == "2020.05.13"


def test_dates_formated():
    date_formated = normalize("d", "date-list(%Y.%m.%d)")(f)

    assert date_formated(["20200513", "20200514"]) == ["2020.05.13", "2020.05.14"]
    assert date_formated("20200513") == ["2020.05.13"]
    assert date_formated([datetime.datetime(2020, 5, 13, 0, 0)]) == ["2020.05.13"]
    assert date_formated([datetime.datetime(2020, 5, 13, 23, 59)]) == ["2020.05.13"]


def test_dates_multiple():
    date_1 = normalize("d", "date-list(%Y.%m.%d)")(f)
    date_2 = normalize("d", "date(%Y.%m.%d)", multiple=True)(f)
    date_3 = normalize("d", "date(%Y.%m.%d)", multiple=False)(f)
    date_4 = normalize("d", "date-list(%Y.%m.%d)", multiple=False)(f)

    assert date_1("20200511") == ["2020.05.11"]
    assert date_2("20200512") == ["2020.05.12"]
    assert date_3("20200513") == "2020.05.13"

    with pytest.raises(ValueError):
        date_4("20200514")


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
