#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

import climetlab as cml
from climetlab.utils.availability import Availability

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_indexing_tmpdir")


def _test_directory_source_availability():
    params = ["z", "t"]
    levels = [500, 850]
    ds = cml.load_source(
        "directory",
        TEST_DIR,
        level=levels,
        variable=params,
        date=20220929,
        time="1200",
    )

    def f():
        for i in ds.index.db.dump_dicts():
            i = {k: v for k, v in i.items() if not k.startswith("_")}
            yield i

    print(len(ds))
    print(ds.availability)


if __name__ == "__main__":
    from climetlab.testing import main

    # main(__file__)
    # test_directory_source_with_none_2(
    # test_directory_source_with_none_1(
    test_directory_source_availability()
    # test_directory_source_order_with_order_by_method_1(
    #    ["z", "t"],
    #    [500, 850],
    # )
