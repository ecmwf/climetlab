#!/usr/bin/env python3

# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import pytest

from climetlab.decorators import normalize
from climetlab.vocabularies.aliases import unalias


def test_unalias():
    assert unalias("grib-paramid", "167") == "2t"
    assert unalias("grib-paramid", "2t") == "2t"


def func_x(x):
    return x


def test_aliases_grib_paramid_mutiple_false():
    aliases_grib_paramid = normalize(
        "x",
        type=str,
        aliases="grib-paramid",
        multiple=False,
    )(func_x)
    assert aliases_grib_paramid("u") == "u"
    assert aliases_grib_paramid(131) == "u"
    assert aliases_grib_paramid("131") == "u"

    # one-element list/tuple
    assert aliases_grib_paramid(("131",)) == "u"
    assert aliases_grib_paramid(["131"]) == "u"

    # list/tuple
    with pytest.raises(TypeError):
        aliases_grib_paramid(["131", "v"])

    # empty list/tuple
    with pytest.raises(TypeError):
        aliases_grib_paramid([])
    with pytest.raises(TypeError):
        aliases_grib_paramid(tuple([]))


def test_aliases_grib_paramid_mutiple_true():
    aliases_grib_paramid = normalize(
        "x",
        type=str,
        aliases="grib-paramid",
        multiple=True,
    )(func_x)
    # single values
    assert aliases_grib_paramid("u") == ["u"]
    assert aliases_grib_paramid(131) == ["u"]
    assert aliases_grib_paramid("131") == ["u"]

    # one-element list/tuple
    assert aliases_grib_paramid(("131",)) == ["u"]
    assert aliases_grib_paramid(["131"]) == ["u"]

    # list/tuple
    assert aliases_grib_paramid(["131", "v"]) == ["u", "v"]
    assert aliases_grib_paramid([131, "v"]) == ["u", "v"]
    assert aliases_grib_paramid(["u", "v"]) == ["u", "v"]
    assert aliases_grib_paramid(("u", "v")) == ["u", "v"]
    assert aliases_grib_paramid([]) == []
    assert aliases_grib_paramid(tuple([])) == []


def test_aliases_grib_paramid_mutiple_none():
    aliases_grib_paramid = normalize(
        "x",
        type=str,
        aliases="grib-paramid",
    )(func_x)
    # single values
    assert aliases_grib_paramid(131) == "u"
    assert aliases_grib_paramid("u") == "u"
    assert aliases_grib_paramid("131") == "u"

    # one-element list/tuple
    assert aliases_grib_paramid(("131",)) == ("u",)
    assert aliases_grib_paramid(["131"]) == ["u"]

    # list/tuple
    assert aliases_grib_paramid(["131", "v"]) == ["u", "v"]
    assert aliases_grib_paramid([131, "v"]) == ["u", "v"]
    assert aliases_grib_paramid(["u", "v"]) == ["u", "v"]
    assert aliases_grib_paramid(("u", "v")) == ("u", "v")
    assert aliases_grib_paramid([]) == []
    assert aliases_grib_paramid(tuple([])) == ()


if __name__ == "__main__":
    # import logging

    # logging.basicConfig(level=logging.WARNING)
    # test_aliases_grib_paramid_mutiple_true()
    # test_aliases_grib_paramid_mutiple_none()
    from climetlab.testing import main

    main(__file__)
