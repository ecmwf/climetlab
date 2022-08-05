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
import shutil

import pytest

import climetlab as cml
from climetlab import settings
from climetlab.core.temporary import temp_directory
from climetlab.scripts.main import CliMetLabApp
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
def test_script_export_cache_cds(capsys):
    export_dir = "tmpdir.test_script_export_cache_cds"
    shutil.rmtree(export_dir, ignore_errors=True)
    os.makedirs(export_dir)

    with temp_directory() as cache_dir:
        with settings.temporary():
            settings.set("cache-directory", cache_dir)

            original = fill_cache_with_cds()

            app = CliMetLabApp()
            app.onecmd(f'export_cache --match "era5" {export_dir}')
            #out, err = capsys.readouterr()
            #print(out)
            #print(err)

            exported_files = glob.glob(os.path.join(export_dir, "*"))
            assert len(exported_files) == 2, exported_files

            target = f"{export_dir}/{os.path.basename(original)}"
            assert filecmp.cmp(original, target), (original, target)

    shutil.rmtree(export_dir)


def test_script_index_directory(capsys):
    directory = "tmpdir.test_script_index_directory"
    shutil.rmtree(directory, ignore_errors=True)
    os.makedirs(directory)
    with temp_directory() as cache_dir:
        with settings.temporary():
            settings.set("cache-directory", cache_dir)

            s1 = cml.load_source("dummy-source", kind="grib", date=20150418)
            assert len(s1) > 0
            os.makedirs(os.path.join(directory, "a"))
            s1.save(os.path.join(directory, "a", "x.grib"))

            s2 = cml.load_source("dummy-source", kind="grib", date=20111202)
            assert len(s2) > 0
            s2.save(os.path.join(directory, "b.grib"))

            files = glob.glob(os.path.join(directory, "*"))
            assert len(files) == 2, files

            app = CliMetLabApp()
            app.onecmd(f"index_directory {directory}")
            out, err = capsys.readouterr()
            assert err == "", err
            print(out)

            s = cml.load_source("directory", directory)
            assert len(s) == len(s1) + len(s2), (len(s1), len(s2), len(s))
            db_path = os.path.abspath(os.path.join(directory, "climetlab.db"))
            assert s.index.db.db_path == db_path

            assert s.to_numpy().mean() == 277.31256510416665

            # to make sure the file descriptors are closed.
            s = None  # noqa: F841
            s1 = None  # noqa: F841
            s2 = None  # noqa: F841

    shutil.rmtree(directory)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
    # test_script_index_directory()
