#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import climetlab as cml

# TODO: choose a smaller dataset


def test_numpy_1():
    ds = cml.load_dataset("weather-bench")
    z500 = ds.to_xarray()
    z = z500.sel({"time": "1979-01-01"}).z.values
    cml.plot_map(z[0], metadata=z500.z)


if __name__ == "__main__":
    test_numpy_1()
