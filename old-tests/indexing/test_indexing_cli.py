#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import shutil
import sys

import numpy as np
import pytest

import climetlab as cml
from climetlab.core.temporary import temp_directory
from climetlab.scripts.main import CliMetLabApp
from climetlab.testing import build_testdata


@pytest.mark.skipif(sys.platform == "win32", reason="Not supported on windows")
def test_indexing_cli_index_directory():
    dir = build_testdata()
    print("Using data in ", dir)

    with temp_directory() as tmpdir:
        shutil.copytree(dir, tmpdir, dirs_exist_ok=True)

        "lsm.grib",
        "pl/climetlab.json",
        "pl/u.grib",
        "pl/v.grib",
        "pl/z.grib",
        "sfc/2t.grib",
        "sfc/climetlab.json",
        "sfc/tp.grib",
        source1 = cml.load_source("file", tmpdir, filter="*.grib")

        app = CliMetLabApp()
        cmd = f"index_directory {tmpdir}"
        app.onecmd(cmd)

        source2 = cml.load_source("indexed-directory", tmpdir)

        source1 = source1.order_by("param", "time", "date")
        source2 = source2.order_by("param", "time", "date")

        assert len(source1) == len(source2)

        for i in range(len(source1)):
            f1 = source1[i]
            f2 = source2[i]
            assert str(f1) == str(f2), (f1, f2)
            assert np.all(f1.to_numpy() == f2.to_numpy())


# def _test_indexing_cli_export_cache():
#     with cd(build_testdata()) as dir:
#         print("Using data in ", dir)
#         with temp_directory() as cache_dir:
#             with settings.temporary():
#                 settings.set("cache-directory", cache_dir)

#             app = CliMetLabApp()
#             app.onecmd(f"index_directory {dir}")
#             # app.onecmd(f'export_cache --match "era5" {export_dir}')

#             exported_files = glob.glob(os.path.join(export_dir, "*"))
#             assert len(exported_files) == 2, exported_files

#             target = f"{export_dir}/{os.path.basename(original)}"
#             assert filecmp.cmp(original, target), (original, target)

#             check_len(source)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
    # test_script_index_directory()
