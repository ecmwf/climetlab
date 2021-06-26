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

from climetlab import load_source


def test_multi_directory_1():
    ds = load_source(
        "file",
        data_file("mixed"),
    )
    print(ds)
    assert len(ds) == 1
    ds.to_xarray()


def test_multi_directory_2():
    ds = load_source(
        "url",
        "file://{}".format(
            data_file("mixed"),
        ),
    )
    print(ds)
    # assert len(ds) == 1


def test_grib_zip():
    # ds =
    load_source(
        "url",
        "file://{}".format(
            data_file("grib.zip"),
        ),
    )
    # assert len(ds) == 1


def test_multi_grib():
    ds = load_source(
        "multi",
        load_source("dummy-source", kind="grib", date=20000101),
        load_source("dummy-source", kind="grib", date=20000102),
    )
    assert len(ds) == 2


def test_multi_grib_mixed():
    ds = load_source(
        "multi",
        load_source("dummy-source", kind="grib", date=20000101),
        load_source("dummy-source", kind="grib", date=20000102),
        load_source("dummy-source", kind="unknown", hello="world"),
    )
    assert len(ds) == 2


if __name__ == "__main__":
    from utils import main

    main(globals())
