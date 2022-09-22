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
import shutil
import sys
import time
import warnings

import pytest

import climetlab as cml
from climetlab.core.temporary import temp_directory, temp_file
from climetlab.decorators import normalize
from climetlab.indexing import PerUrlIndex
from climetlab.readers.grib.index import FieldSet
from climetlab.testing import climetlab_file
from climetlab.utils.serialise import SERIALISATION, deserialise_state, serialise_state

here = os.path.dirname(__file__)
sys.path.insert(0, here)
from indexing_fixtures import check_sel_and_order, get_fixtures


@pytest.mark.parametrize("params", (["t", "u"], ["u", "t"]))
@pytest.mark.parametrize("levels", ([500, 850], [850, 500]))
@pytest.mark.parametrize(
    "source_name",
    [
        "directory",
        # "list-of-dicts",
        # "file",
    ],
)
def test_indexing_pickle(params, levels, source_name):
    request = dict(
        level=levels,
        variable=params,
        date=20220921,
        time="1200",
    )

    ds, __tmp, total, n = get_fixtures(source_name, {})
    assert len(ds) == total, len(ds)

    ds = ds.sel(**request)
    ds = ds.order_by(level=levels, variable=params)

    assert len(ds) == n, (len(ds), ds, SERIALISATION)
    state = serialise_state(ds)
    ds = deserialise_state(state)
    assert len(ds) == n, (len(ds), ds, SERIALISATION)

    check_sel_and_order(ds, params, levels)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
