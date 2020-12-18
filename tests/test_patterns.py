# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.utils.patterns import Pattern


def test_patterns():

    p = Pattern("{date:date(%Y%m%d)}-{param}-{level:int}-{level:int(%03d)}")

    assert p.names == ["date", "level", "param"], p.names

    assert (
        p.substitute(dict(date="2000-01-01", param="2t", level=12))
        == "20000101-2t-12-012"
    )

    p = Pattern("{variable:enum(2t,tp)}.{type:enum(rt,hc)}.{date:date(%Y%m%d)}.grib")
    assert (
        p.substitute(dict(date="2000-01-01", variable="tp", type="rt"))
        == "tp.rt.20000101.grib"
    )

    assert p.substitute(dict(date="2000-01-01", variable=["tp", "2t"], type="rt")) == [
        "tp.rt.20000101.grib",
        "2t.rt.20000101.grib",
    ]


if __name__ == "__main__":
    test_patterns()
