#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import pytest

from climetlab.decorators import availability
from climetlab.decorators import normalize


def name_no_default(name):
    return name


@pytest.mark.skip("Not implemented yet")
def test_enum_2_normalizers():
    g = name_no_default
    g = normalize("a", [1, 2])(g)
    g = normalize("a", [3, 4])(g)
    with pytest.raises(ValueError, "Duplicate normalize decorators"):
        g(a=1)


C3 = [
    {"name": "50"},
    {"name": "100"},
]


@pytest.mark.skip("Not implemented yet")
def test_enum_inconsistent_availablity_normalizers():
    g = name_no_default
    g = normalize("name", type=int)(g)
    g = availability(C3)(g)
    g(name="50")
    with pytest.raises(
        ValueError,
        match="Inconsistent types for availability and normalize for argument 'a'.",
    ):
        g(name="50")


def test_enum_no_type():
    g = normalize("name", multiple=True)(name_no_default)
    assert g(["a", "b"]) == ["a", "b"]
    assert g("a") == ["a"]


# def test_enum_cannot_find_type_2():
#     g = normalize("name", type="zzz")(name_no_default)
#     with pytest.raises(ValueError, match="Cannot infer type .*"):
#         g(["a", "b"])
#
#
# def test_enum_cannot_find_type_3():
#     g = normalize("name", type="zzz", multiple=True)(name_no_default)
#     with pytest.raises(ValueError, match="Cannot infer type .*"):
#         g(["a", "b"])


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
