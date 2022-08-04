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

def fill_cache_with_cds():
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
    path = s.path

    assert len(s) == 2

    return path

@pytest.mark.skipif(NO_CDS, reason="No access to CDS")
def test_script_export_cache_cds():
    # Since we are using a system call to test the script,
    # the actual settings file is modified
    # The value of cache-directory is set back to its original value
    # using a try/finally
    original_cachedir = settings.get("cache-directory")
    with temp_directory() as export_dir:
        with temp_directory(), temp_directory() as cache_dir:
            with settings.temporary():
                settings.set("cache-directory", cache_dir)
                cmd = f"climetlab settings cache-directory {cache_dir}"
                out = subprocess.check_output(cmd.split(" ")).decode("utf-8")
                print(cmd, out)

                try:
                    path_in_cache = fill_cache_with_cds()

                    cmd = f'climetlab export_cache --match "era5" --directory {export_dir}'
                    out = subprocess.check_output(cmd.split(" ")).decode("utf-8")
                    print(cmd, out)
                finally:
                    cmd = f"climetlab settings cache-directory {original_cachedir}"
                    subprocess.check_output(cmd.split(" ")).decode("utf-8")

                exported_files = glob.glob(f"{export_dir}/*")
                assert len(exported_files) == 2, exported_files

                path_in_target = f"{export_dir}/{os.path.basename(path_in_cache)}"
                assert filecmp.cmp(
                    path_in_cache, path_in_target
                ), f"Exported {path_in_target} differs from original file {path_in_cache}"

def test_script_export_cache_cds():
    # Since we are using a system call to test the script,
    # the actual settings file is modified
    # The value of cache-directory is set back to its original value
    # using a try/finally
    original_cachedir = settings.get("cache-directory")
    with temp_directory() as export_dir:
        with temp_directory(), temp_directory() as cache_dir:
            with settings.temporary():
                settings.set("cache-directory", cache_dir)
                cmd = f"climetlab settings cache-directory {cache_dir}"
                out = subprocess.check_output(cmd.split(" ")).decode("utf-8")
                print(cmd, out)

                try:
                    path_in_cache = fill_cache()

                    cmd = f'climetlab export_cache --match "era5" --directory {export_dir}'
                    out = subprocess.check_output(cmd.split(" ")).decode("utf-8")
                    print(cmd, out)
                finally:
                    cmd = f"climetlab settings cache-directory {original_cachedir}"
                    subprocess.check_output(cmd.split(" ")).decode("utf-8")

                exported_files = glob.glob(os.path.join(export_dir, "*"))
                assert len(exported_files) == 2, exported_files

                path_in_target = f"{export_dir}/{os.path.basename(path_in_cache)}"
                assert filecmp.cmp(
                    path_in_cache, path_in_target
                ), f"Exported {path_in_target} differs from original file {path_in_cache}"

if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
    # test_script_export_cache_cds()
