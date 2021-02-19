#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import sys
from climetlab import load_source, source
import pytest


def test_file_source_1():
    load_source("file", "docs/examples/test.grib")


@pytest.mark.skipif(sys.version_info < (3, 7), reason="Version 3.7 or greater needed")
def test_file_source_2():
    source.file("docs/examples/test.grib")


def zarr_not_installed():
    try:
        import zarr
        import s3fs

        return False
    except ImportError:
        return True


@pytest.mark.skipif(zarr_not_installed(), reason="Zarr or S3FS not installed")
def test_zarr_source():
    source = load_source(
        "zarr-s3",
        "https://storage.ecmwf.europeanweather.cloud/s2s-ai-competition/data/zarr/2t.zarr",
    )
    source.to_xarray()
