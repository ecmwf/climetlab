#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab import load_source, plot_map


def test_grib():
    for s in load_source("file", "docs/examples/test.grib"):
        plot_map(s)

        # test.grib fields endStep is 0, so datetime == valid_datetime
        assert s.datetime() == s.valid_datetime()

        # test shape
        assert s.shape == (11, 19)


if __name__ == "__main__":
    test_grib()
