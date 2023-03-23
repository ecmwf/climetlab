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
import sys

import pytest

import climetlab as cml
from climetlab.core.temporary import temp_file

here = os.path.dirname(__file__)
sys.path.insert(0, here)
from indexing_fixtures import check_sel_and_order, get_fixtures  # noqa: E402


@pytest.mark.skipif(sys.platform == "win32", reason="Cannot unlink tmp file on Windows")
@pytest.mark.parametrize("params", (["t", "u"], ["u", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
@pytest.mark.parametrize(
    "source_name", ["indexed-directory", "file", "indexed-url", "indexed-urls"]
)
def test_indexing_save(params, levels, source_name):
    request = dict(
        level=levels,
        variable=params,
        date=20220929,
        time="1200",
    )
    if (
        source_name == "indexed-url" or source_name == "indexed-urls"
    ):  # TODO: make all test data consistent
        request["date"] = "19970101"
        request["time"] = [1100, 1200]

    ds, _, total, n = get_fixtures(source_name, {})
    assert len(ds) == total, len(ds)

    ds = ds.sel(**request)
    assert len(ds) == n, len(ds)

    ds = ds.order_by(level=levels, variable=params)
    assert len(ds) == n, len(ds)

    if not (
        source_name == "indexed-url" or source_name == "indexed-urls"
    ):  # TODO: make all test data consistent
        check_sel_and_order(ds, params, levels)

    with temp_file() as filename:
        ds.save(filename)
        ds = cml.load_source("file", filename)

        assert len(ds) == n
        if not (
            source_name == "indexed-url" or source_name == "indexed-urls"
        ):  # TODO: make all test data consistent
            check_sel_and_order(ds, params, levels)


if __name__ == "__main__":
    from climetlab.testing import main

    # test_indexing_save(["t", "u"], [500, 850], "indexed-url")

    main(__file__)
