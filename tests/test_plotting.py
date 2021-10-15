#!/usr/bin/env python3

# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import pytest

import climetlab as cml
from climetlab.testing import climetlab_file


def test_plot_1():
    s = cml.load_source("file", climetlab_file("docs/examples/test.grib"))
    assert cml.plot_map(s) is None

    assert cml.plot_map(s[0]) is None

    p = cml.new_plot()
    p.plot_map(s[0])
    p.plot_map(s[1])

    assert p.show() is None

    with pytest.raises(TypeError):
        cml.plot_map(s, unknown=42)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
