#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from climetlab import load_source
from climetlab.testing import climetlab_file


def test_file_source_grib():

    s = load_source("file", climetlab_file("docs/examples/test.grib"))
    assert len(s) == 2


def test_file_source_netcdf():
    s = load_source("file", climetlab_file("docs/examples/test.nc"))
    assert len(s) == 2


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
