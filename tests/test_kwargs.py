#!/usr/bin/env python3

# (C} Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from climetlab.utils.kwargs import merge_dicts


def test_merge_dicts():
    assert merge_dicts({"a": 1, "b": 2}, {"a": 1, "b": 6}) == {"a": 1, "b": 6}
    assert merge_dicts({"a": 1}, {"a": 1, "b": 6}) == {"a": 1, "b": 6}
    assert merge_dicts({"a": 1, "b": 2}, {"a": 3}) == {"a": 3, "b": 2}
    assert merge_dicts({"a": 1, "b": 2}, {"c": 3}) == {"a": 1, "b": 2, "c": 3}

    assert merge_dicts({"a": {"b": 2}}, {"c": 3}) == {"a": {"b": 2}, "c": 3}
    assert merge_dicts({"a": {"b": 2}}, {"a": {"c": 4}}) == {"a": {"b": 2, "c": 4}}


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
