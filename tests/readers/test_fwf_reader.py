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

import climetlab as cml


@pytest.mark.external_download
@pytest.mark.download
def test_fwf():
    url = "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/monthly.ao.index.b50.current.ascii"

    s = cml.load_source(
        "url",
        url,
        reader="fix_width_format",
    )

    print(s.to_pandas())


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
