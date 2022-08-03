#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import filecmp
import glob
import os
import subprocess

import pytest

import climetlab as cml
from climetlab import settings
from climetlab.core.temporary import temp_directory
from climetlab.testing import NO_CDS


@pytest.mark.skipif(NO_CDS, reason="No access to CDS")
def test_script_export_cache_cds():
    with temp_directory() as cachedir:
        with settings.temporary():
            settings.set("cache-directory", cachedir)

            cml.load_source(
                "cds",
                "reanalysis-era5-single-levels",
                variable=["2t", "msl"],
                product_type="reanalysis",
                area=[50, -50, 20, 50],
                date="2011-12-02",
                time="12:00",
            )

            s = cml.load_source(
                "cds",
                "reanalysis-era5-single-levels",
                variable=["2t", "msl"],
                product_type="reanalysis",
                area=[50, -50, 20, 50],
                date="2008-07-19",
                time="12:00",
            )
            origin = s.path

            assert len(s) == 2

            with temp_directory() as exportdir:
                cmd = f'climetlab export_cache --match "era5" --directory {exportdir}'
                subprocess.check_output(cmd.split(" ")).decode("utf-8")

                exported_files = glob.glob(f"{exportdir}/*")
                assert len(exported_files) == 2, exported_files

                target = f"{exportdir}/{os.path.basename(origin)}"
                assert filecmp.cmp(
                    origin, target
                ), f"Exported {target} differs from original file {origin}"


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
    # test_script_export_cache_cds()
