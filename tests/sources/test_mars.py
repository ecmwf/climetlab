#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import pytest

from climetlab import load_source
from climetlab.testing import NO_MARS


@pytest.mark.skipif(NO_MARS, reason="No access to MARS")
def test_mars_grib():
    s = load_source(
        "mars",
        param=["2t", "msl"],
        levtype="sfc",
        area=[50, -50, 20, 50],
        grid=[1, 1],
        date="2012-12-13",
    )
    assert len(s) == 2


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
