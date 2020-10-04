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


def test_netcdf():
    for s in load_source("file", "docs/examples/test.nc"):
        plot_map(s)


if __name__ == "__main__":
    test_netcdf()
