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


def func_x(x):
    return x


@pytest.mark.parametrize("typ", [str, int, float])
def test_aliases_grib_paramid_mutiple_false(typ):
    _131 = typ(131)
    aliases_grib_paramid = normalize(
        "x",
        type=typ,
        aliases={"u": typ(131), "v": typ(132)},
        multiple=False,
    )(func_x)
    assert aliases_grib_paramid("u") == _131
    assert aliases_grib_paramid(131) == _131
    assert aliases_grib_paramid("131") == _131

    # one-element list/tuple
    assert aliases_grib_paramid(("131",)) == _131
    assert aliases_grib_paramid(["131"]) == _131

    # list/tuple
    with pytest.raises(TypeError):
        aliases_grib_paramid(["131", "v"])

    # empty list/tuple
    with pytest.raises(TypeError):
        aliases_grib_paramid([])
    with pytest.raises(TypeError):
        aliases_grib_paramid(tuple([]))


@pytest.mark.parametrize(
    "typ,_131,_132", [(str, "131", "132"), (int, 131, 132), (float, 131.0, 132.0)]
)
def test_aliases_grib_paramid_mutiple_true(typ, _131, _132):
    aliases_grib_paramid = normalize(
        "x",
        type=typ,
        aliases={"u": typ(131), "v": typ(132)},
        multiple=True,
    )(func_x)
    # single values
    assert aliases_grib_paramid("u") == [_131]
    assert aliases_grib_paramid(131) == [_131]
    assert aliases_grib_paramid("131") == [_131]

    # one-element list/tuple
    assert aliases_grib_paramid(("131",)) == [_131]
    assert aliases_grib_paramid(["131"]) == [_131]

    # list/tuple
    assert aliases_grib_paramid(["131", "v"]) == [_131, _132]
    assert aliases_grib_paramid([131, "v"]) == [_131, _132]
    assert aliases_grib_paramid(["u", "v"]) == [_131, _132]
    assert aliases_grib_paramid(("u", "v")) == [_131, _132]
    assert aliases_grib_paramid([]) == []
    assert aliases_grib_paramid(tuple([])) == []


@pytest.mark.parametrize(
    "typ,_131,_132", [(str, "131", "132"), (int, 131, 132), (float, 131.0, 132.0)]
)
def test_aliases_mutiple_none(typ, _131, _132):
    aliases_func = normalize(
        "x",
        type=typ,
        aliases={"u": _131, "v": _132},
    )(func_x)
    # single values
    assert aliases_func("u") == _131
    assert aliases_func(131) == _131
    assert aliases_func("131") == _131

    # one-element list/tuple
    assert aliases_func(("131",)) == (_131,)
    assert aliases_func(["131"]) == [_131]

    # list/tuple
    assert aliases_func(["131", "v"]) == [_131, _132]
    assert aliases_func([131, "v"]) == [_131, _132]
    assert aliases_func(["u", "v"]) == [_131, _132]
    assert aliases_func(("u", "v")) == (_131, _132)
    assert aliases_func([]) == []
    assert aliases_func(tuple([])) == ()


def test_aliases():
    @normalize("x", aliases={"one": 1})
    def f(x):
        return x

    assert f(1) == 1
    assert f("one") == 1


if __name__ == "__main__":
    # import logging
    # logging.basicConfig(level=logging.WARNING)
    # test_aliases_grib_paramid_mutiple_true()
    from climetlab.testing import main

    main(__file__)
