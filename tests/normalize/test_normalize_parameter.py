#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.decorators import normalize


def test_param_convention_mars_1():
    @normalize("parameter", "variable-list", convention="mars")
    def values_mars(parameter):
        return parameter

    assert values_mars(parameter="tp") == ["tp"]
    assert values_mars(parameter="2t") == ["2t"]
    assert values_mars(parameter="t2m") == ["2t"]
    assert values_mars(parameter=["t2m", "tp"]) == ["2t", "tp"]
    assert values_mars(parameter="whatever") == ["whatever"]


def test_param_convention_mars_2():
    @normalize("parameter", "variable-list(mars)")
    def values_mars(parameter):
        return parameter

    assert values_mars(parameter="tp") == ["tp"]
    assert values_mars(parameter="2t") == ["2t"]
    assert values_mars(parameter="t2m") == ["2t"]
    assert values_mars(parameter=["t2m", "tp"]) == ["2t", "tp"]
    assert values_mars(parameter="whatever") == ["whatever"]


def test_param_convention_cf_list():
    @normalize("parameter", "variable-list(cf)")
    def values_cf(parameter):
        return parameter

    assert values_cf(parameter="tp") == ["tp"]
    assert values_cf(parameter="2t") == ["t2m"]
    assert values_cf(parameter="t2m") == ["t2m"]


def test_param_convention_cf():
    @normalize("parameter", "variable(cf)")
    def values_cf(parameter):
        return parameter

    assert values_cf(parameter="tp") == "tp"
    assert values_cf(parameter="2t") == "t2m"
    assert values_cf(parameter="t2m") == "t2m"


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
