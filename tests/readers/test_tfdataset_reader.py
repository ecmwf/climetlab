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
from climetlab.testing import MISSING
from climetlab.testing import TEST_DATA_URL


@pytest.mark.skipif(MISSING("tensorflow"), reason="No tensorflow")
@pytest.mark.download
def test_download_tfdataset():
    ds = load_source(
        "url-pattern",
        "{url}/fixtures/tfrecord/EWCTest0.{n}.tfrecord",
        n=[0, 1],
        url=TEST_DATA_URL,
        # TODO: move adapt test data creation script
        # url=f"{TEST_DATA_URL}/input/",
    )

    ds.graph()
    assert len(ds) == 200, len(ds)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
