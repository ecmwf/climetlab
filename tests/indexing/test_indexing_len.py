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

from indexing_generic import build_testdata, cd, TEST_DATA_URL


def check_len(source):
    assert len(source) == 337


def test_indexing_len_for_source_file():
    with cd(build_testdata()) as dir:
        print("Using data in ", dir)

        source = cml.load_source("file", "all.grib")
        check_len(source)


def test_indexing_len_for_source_url():
    source = cml.load_source("url", f"{TEST_DATA_URL}/all.grib")
    check_len(source)

def test_indexing_len_for_source_multi():
    with cd(build_testdata()) as dir:
        print("Using data in ", dir)

        pl = cml.load_source("file", 'pl', filter='*.grib')
        sfc = cml.load_source("file", 'sfc', filter='*.grib')
        lsm = cml.load_source("file", 'lsm.grib')
        source = cml.load_source("multi", [pl, sfc, lsm])

        check_len(source)

if __name__ == "__main__":
    # from climetlab.testing import main

    # main(__file__)
    test_indexing_len_for_source_url()
    test_indexing_len_for_source_file()
