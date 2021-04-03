#!/usr/bin/env python3

# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.utils.factorise import factorise

C0 = [
    {"level": "500", "param": "Z", "step": "24"},
    {"level": "500", "param": "Z", "step": "36"},
    {"level": "500", "param": "Z", "step": "48"},
    {"level": "500", "param": "T", "step": "24"},
    {"level": "500", "param": "T", "step": "36"},
    {"level": "500", "param": "T", "step": "48"},
    {"level": "850", "param": "T", "step": "36"},
    {"level": "850", "param": "T", "step": "48"},
    {"level": "1000", "param": "Z", "step": "24"},
    {"level": "1000", "param": "Z", "step": "48"},
]

C1 = [
    {"level": ["1000"], "param": ["Z"], "step": ["24", "48"]},
    {"level": ["500"], "param": ["T", "Z"], "step": ["24", "36", "48"]},
    {"level": ["850"], "param": ["T"], "step": ["36", "48"]},
]


def _(x):
    """ Make list of dicts comparable """

    def __(r):
        for k, v in sorted(r.items()):
            yield (k, tuple(sorted(v)))

    return tuple(sorted(tuple(__(a)) for a in x))


def test_factorise_1():
    f = factorise(C0)
    assert _(f.to_list()) == _(C1)

    assert f.unique_values == {
        "param": {"Z", "T"},
        "level": {"500", "850", "1000"},
        "step": {"36", "48", "24"},
    }


def test_factorise_2():
    assert _(factorise(C1).to_list()) == _(C1)
    assert _(factorise(C1 + C0).to_list()) == _(C1)


def test_factorise_3():

    c = factorise(
        [
            {"date": ["1990-01-01/1990-01-02"]},
            {"date": ["1990-01-02/1990-01-05"]},
            {"date": ["1990-01-04/1990-01-15"]},
        ],
        intervals=["date"],
    ).to_list()

    assert _(c) == _([{"date": ["1990-01-01/1990-01-15"]}])

    c = factorise(
        [
            {"date": ["1990-01-01/1990-01-02"]},
            {"date": ["1990-01-04/1990-01-15"]},
        ],
        intervals=["date"],
    ).to_list()

    assert _(c) == _([{"date": ["1990-01-01/1990-01-02", "1990-01-04/1990-01-15"]}])

    c = factorise(
        [
            {"date": ["1990-01-01/1990-01-10"]},
            {"date": ["1990-01-04/1990-01-15"]},
        ],
        intervals=["date"],
    ).to_list()

    assert _(c) == _([{"date": ["1990-01-01/1990-01-15"]}])


if __name__ == "__main__":
    # test_factorise_1()
    test_factorise_2()
