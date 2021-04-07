#!/usr/bin/env python3

# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime

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
    c = factorise(C0)
    assert _(c.to_list()) == _(C1)

    assert c.unique_values() == {
        "level": ("1000", "500", "850"),
        "param": ("T", "Z"),
        "step": ("24", "36", "48"),
    }

    assert sum(1 for x in c.iterate(False)) == 3
    assert sum(1 for x in c.iterate(True)) == 10

    assert c.select(param="T").count() == 5
    assert c.select(param="Z").count() == 5
    assert c.select(param="Z", step="24").count() == 2
    assert c.select(param="Z", step="99").count() == 0

    assert c.count(param="T") == 5
    assert c.count(param="Z") == 5
    assert c.count(param="Z", step="24") == 2
    assert c.count(param="Z", step="99") == 0


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
    )

    assert _(c.to_list()) == _([{"date": ["1990-01-01/1990-01-15"]}])

    c = factorise(
        [
            {"date": ["1990-01-01/1990-01-02"]},
            {"date": ["1990-01-04/1990-01-15"]},
        ],
        intervals=["date"],
    )

    assert _(c.to_list()) == _(
        [{"date": ["1990-01-01/1990-01-02", "1990-01-04/1990-01-15"]}]
    )

    assert c.count() == 14

    c = factorise(
        [
            {"date": ["1990-01-01/1990-01-10"]},
            {"date": ["1990-01-04/1990-01-15"]},
        ],
        intervals=["date"],
    )

    assert _(c.to_list()) == _([{"date": ["1990-01-01/1990-01-15"]}])

    assert c.count() == 15


def test_factorise_4():

    c = factorise(
        [
            {"date": ["1990-01-01/1990-01-02"], "param": ["Z", "T"]},
            {"date": ["1990-01-02/1990-01-05"], "param": ["Z"]},
            {"date": ["1990-01-04/1990-01-15"], "param": ["Z", "T"]},
        ],
        intervals=["date"],
    )

    assert _(c.to_list()) == _(
        [
            {"date": ["1990-01-01/1990-01-15"], "param": ["Z"]},
            {
                "date": ["1990-01-01/1990-01-02", "1990-01-04/1990-01-15"],
                "param": ["T"],
            },
        ]
    )

    assert c.count() == 29
    assert c.count(param="Z") == 15
    assert c.count(date="1990-01-01") == 2
    assert c.select(param="T").count() == 14
    assert c.select(date="1990-01-01").count() == 2
    assert c.select(date="1990-01-01").select(param="Z").count() == 1

    assert _(c.select(date="1990-01-01").to_list()) == _(
        [{"date": ["1990-01-01"], "param": ["T", "Z"]}]
    )

    assert _(c.select(date="1990-01-02/1990-01-05").to_list()) == _(
        [
            {
                "date": ["1990-01-02", "1990-01-04/1990-01-05"],
                "param": ["T"],
            },
            {"date": ["1990-01-02/1990-01-05"], "param": ["Z"]},
        ]
    )

    E = [
        {"date": datetime.date(1990, 1, 2), "param": "T"},
        {"date": datetime.date(1990, 1, 4), "param": "T"},
        {"date": datetime.date(1990, 1, 2), "param": "Z"},
        {"date": datetime.date(1990, 1, 3), "param": "Z"},
        {"date": datetime.date(1990, 1, 4), "param": "Z"},
    ]

    for r, e in zip(c.select(date="1990-01-02/1990-01-04").iterate(True), E):
        assert r == e

    assert _(c.missing(param="T", date="1990-01-01/1990-01-15").to_list()) == _(
        [{"date": ["1990-01-03"], "param": ["T"]}]
    )


if __name__ == "__main__":
    for k, f in sorted(globals().items()):
        if k.startswith("test_") and callable(f):
            print(k)
            f()
