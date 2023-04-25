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

from climetlab import load_source
from climetlab.testing import climetlab_file


def test_constant():
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
        "sin_local_time",
    ]

    ds = load_source(
        "constants",
        sample,
        date=dates,
        param=params,
    )

    ds = ds.order_by("param", "valid_datetime")

    assert len(ds) == len(params) * len(dates)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
