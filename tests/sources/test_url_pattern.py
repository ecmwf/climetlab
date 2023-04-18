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


@pytest.mark.download
def test_url_pattern_source_3():
    source = load_source(
        "url-pattern",
        "https://github.com/ecmwf/climetlab/raw/main/docs/examples/test.{format}",
        {"format": ["nc", "grib"]},
    )
    # note that both files contain the same data
    assert len(source) == 4
    for i in source:
        print(i)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
