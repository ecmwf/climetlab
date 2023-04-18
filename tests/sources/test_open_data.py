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
from climetlab.testing import NO_EOD


@pytest.mark.skipif(NO_EOD, reason="No access to Open data")
@pytest.mark.download
def test_open_data():
    s = load_source(
        "ecmwf-open-data",
        step=240,
        type="fc",
        param="msl",
    )
    print(s.path)


if __name__ == "__main__":
    # test_open_data()
    from climetlab.testing import main

    main(__file__)
