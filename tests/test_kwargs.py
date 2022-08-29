#!/usr/bin/env python3

# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from climetlab.utils.kwargs import merge_dicts


def test_merge_dicts():

    assert merge_dicts(dict(a=1, b=2), dict(a=1, b=6)) == dict(a=1, b=6)
    assert merge_dicts(dict(a=1), dict(a=1, b=6)) == dict(a=1, b=6)
    assert merge_dicts(dict(a=1, b=2), dict(a=3)) == dict(a=3, b=2)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
