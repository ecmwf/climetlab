#!/usr/bin/env python3

# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime

import numpy as np

from climetlab import load_source
from climetlab.testing import climetlab_file


def test_constant_1():
    sample = load_source("file", climetlab_file("docs/examples/test.grib"))

    start = sample[0].datetime()
    first_step = 6
    last_step = 240
    step_increment = 6
    dates = []
    for step in range(first_step, last_step + step_increment, step_increment):
        dates.append(start + datetime.timedelta(hours=step))

    params = [
        "cos_latitude",
        "cos_longitude",
        "sin_latitude",
        "sin_longitude",
        "cos_julian_day",
        "cos_local_time",
        "sin_julian_day",
        "cos_solar_zenith_angle",
    ]

    ds = load_source(
        "constants",
        sample,
        date=dates,
        param=params,
    )

    ds = ds.order_by("param", "valid_datetime")

    assert len(ds) == len(params) * len(dates)


def test_constant_2():
    sample = load_source("file", climetlab_file("docs/examples/test.grib"))

    start = sample[0].datetime()
    start = datetime.datetime(start.year, start.month, start.day)
    first_step = 1
    last_step = 10
    step_increment = 1
    dates = []
    for step in range(first_step, last_step + step_increment, step_increment):
        dates.append(start + datetime.timedelta(days=step))

    params = [
        "cos_latitude",
        "cos_longitude",
        "sin_latitude",
        "sin_longitude",
        "cos_julian_day",
        "cos_local_time",
        "sin_julian_day",
        "cos_solar_zenith_angle",
    ]

    ntimes = 4
    ds = load_source(
        "constants",
        sample,
        date=dates,
        time=f"0/to/18/by/{24//ntimes}",
        param=params,
    )

    ds = ds.order_by("param", "valid_datetime")

    assert len(ds) == len(params) * len(dates) * ntimes


def test_constant_3():
    sample = load_source("file", climetlab_file("docs/examples/test.grib"))

    date = sample[0].datetime()
    date_plus_6h = date + datetime.timedelta(hours=6)
    a = load_source("constants", sample, date=date_plus_6h, param="cos_solar_zenith_angle")
    b = load_source("constants", sample, date=date, param="cos_solar_zenith_angle+6h")
    assert np.all(a.to_numpy() == b.to_numpy())
    assert a[0].metadata("param") == "cos_solar_zenith_angle"
    assert b[0].metadata("param") == "cos_solar_zenith_angle+6h"

    date = sample[0].datetime()
    date_minus_30d = date + datetime.timedelta(days=-30)
    a = load_source("constants", sample, date=date_minus_30d, param="cos_solar_zenith_angle")
    b = load_source("constants", sample, date=date, param="cos_solar_zenith_angle-30d")
    assert np.all(a.to_numpy() == b.to_numpy())
    assert a[0].metadata("param") == "cos_solar_zenith_angle"
    assert b[0].metadata("param") == "cos_solar_zenith_angle-30d"


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
