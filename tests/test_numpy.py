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

"""
Test if a numpy array can be plotted using another field as metadata,
i.e. for bounding box, style, etc.
"""


# def test_numpy_grib():
#     s = cml.load_source("file", "docs/examples/test.grib")
#     x = s.to_xarray()
#     cml.plot_map(x.msl.values, metadata=s[1])


# def test_numpy_netcdf():
#     s = cml.load_source("file", "docs/examples/test.nc")
#     x = s.to_xarray()
#     cml.plot_map(x.msl.values, metadata=s[1])


def test_numpy_xarray():
    s = cml.load_source("file", "docs/examples/test.nc")
    x = s.to_xarray()
    cml.plot_map(x.msl.values, metadata=x.msl)


if __name__ == "__main__":
    test_numpy_xarray()
