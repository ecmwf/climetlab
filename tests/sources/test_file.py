#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging
import os
import sys

import pytest

from climetlab import load_source
from climetlab.core.temporary import temp_directory
from climetlab.testing import climetlab_file

LOG = logging.getLogger(__name__)


def test_file_source_grib():
    s = load_source("file", climetlab_file("docs/examples/test.grib"))
    assert len(s) == 2


def test_file_source_netcdf():
    s = load_source("file", climetlab_file("docs/examples/test.nc"))
    assert len(s) == 2


def test_user_1():
    s = load_source("file", climetlab_file("docs/examples/test.grib"))
    home_file = os.path.expanduser("~/.climetlab/test.grib")
    try:
        s.save(home_file)
        # Test expand user
        s = load_source("file", "~/.climetlab/test.grib")
        assert len(s) == 2
    finally:
        try:
            os.unlink(home_file)
        except OSError:
            LOG.exception("unlink(%s)", home_file)


@pytest.mark.skipif(sys.platform == "win32", reason="Cannot (yet) use expandvars on Windows")
def test_user_2():
    s = load_source("file", climetlab_file("docs/examples/test.grib"))
    home_file = os.path.expanduser("~/.climetlab/test.grib")
    try:
        s.save(home_file)
        # Test expand vars
        s = load_source("file", "$HOME/.climetlab/test.grib", expand_vars=True)
        assert len(s) == 2
    finally:
        try:
            os.unlink(home_file)
        except OSError:
            LOG.exception("unlink(%s)", home_file)


def test_glob():
    s = load_source("file", climetlab_file("docs/examples/test.grib"))
    with temp_directory() as tmpdir:
        s.save(os.path.join(tmpdir, "a.grib"))
        s.save(os.path.join(tmpdir, "b.grib"))

        s = load_source("file", os.path.join(tmpdir, "*.grib"))
        assert len(s) == 4, len(s)

        s = load_source("file", tmpdir)
        assert len(s) == 4, len(s)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
