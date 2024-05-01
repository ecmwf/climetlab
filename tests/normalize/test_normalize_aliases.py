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

from climetlab.decorators import alias_argument
from climetlab.decorators import normalize


def func_x(x):
    return x


def func_xy(x, y):
    return x, y


def func_xyz(x, y, z):
    return x, y, z


def test_alias_argument_1():
    f = alias_argument()(func_x)
    assert f(1) == 1
    assert f(x=1) == 1
    with pytest.raises(TypeError):
        assert f(unk=1) == 1

    f = alias_argument(x=["alias"])(func_x)
    assert f(alias=1) == 1
    assert f(x=1) == 1

    f = alias_argument(x="alias")(func_x)
    assert f(alias=1) == 1
    assert f(x=1) == 1

    with pytest.raises(ValueError):
        f = alias_argument(x={"alias": "value"})(func_x)

    f = alias_argument(x=["alias", "blias"])(func_x)
    assert f(alias=1) == 1

    with pytest.raises(TypeError):
        f = alias_argument(unk=["x"])(func_x)
        assert f(x=1) == 1


def test_alias_argument_1_bis():
    f = alias_argument("x", ["alias"])(func_x)
    assert f(alias=1) == 1

    f = alias_argument("x", "alias")(func_x)
    assert f(alias=1) == 1


def test_alias_argument_2_bis():
    f = alias_argument("x", ["alias_x"])(func_xy)
    f = alias_argument("y", ["alias_y"])(f)
    assert f(alias_x=1, alias_y=2) == (1, 2)


def test_alias_argument_2():
    f = alias_argument(y=["alias", "blias"])(func_xy)
    assert f(1, alias=2) == (1, 2)

    f = alias_argument(y=["alias", "blias"])(func_xy)
    assert f(1, alias=2) == (1, 2)
    assert f(1, blias=2) == (1, 2)
    assert f(1, y=2) == (1, 2)
    assert f(x=1, alias=2) == (1, 2)
    assert f(x=1, blias=2) == (1, 2)
    assert f(x=1, y=2) == (1, 2)


def test_alias_argument_3():
    f = alias_argument(y=["alias", "blias"])(func_xyz)
    assert f(1, alias=2, z=3) == (1, 2, 3)
    assert f(1, blias=2, z=3) == (1, 2, 3)
    assert f(z=3, alias=2, x=1) == (1, 2, 3)
    assert f(x=1, alias=2, z=3) == (1, 2, 3)
    assert f(x=1, z=3, blias=2) == (1, 2, 3)
    assert f(x=1, y=2, z=3) == (1, 2, 3)

    f = alias_argument(y=["y_alias"], x=["x_alias"])(func_xyz)
    assert f(y_alias=2, x_alias=1, z=3) == (1, 2, 3)

    with pytest.raises(ValueError):
        f = alias_argument(x=["alias"], y=["alias"])(func_xyz)
    with pytest.raises(ValueError):
        f = alias_argument(x=["alias", "blias"], y=["alias"])(func_xyz)
    with pytest.raises(ValueError):
        f = alias_argument(x=["alias", "blias"], y=["alias", "blias"])(func_xyz)


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


@pytest.mark.parametrize("typ,_131,_132", [(str, "131", "132"), (int, 131, 132), (float, 131.0, 132.0)])
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


@pytest.mark.parametrize("typ,_131,_132", [(str, "131", "132"), (int, 131, 132), (float, 131.0, 132.0)])
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
