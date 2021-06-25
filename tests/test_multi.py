#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from utils import data_file

import climetlab as cml


def test_multi_directory_1():
    ds = cml.load_source(
        "file",
        data_file("mixed"),
    )
    print(ds)
    assert len(ds) == 1
    ds.to_xarray()


def test_multi_directory_2():
    ds = cml.load_source(
        "url",
        "file://{}".format(
            data_file("mixed"),
        ),
    )
    print(ds)
    # assert len(ds) == 1


def test_grib_zip():
    # ds =
    cml.load_source(
        "url",
        "file://{}".format(
            data_file("grib.zip"),
        ),
    )
    # assert len(ds) == 1


if __name__ == "__main__":
    for k, f in sorted(globals().items()):
        if k.startswith("test_") and callable(f):
            print(k)
            f()
