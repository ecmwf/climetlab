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
def test_this():
    export_dir = "dev.tmpdir.test_script_export_cache_cds"
    shutil.rmtree(export_dir, ignore_errors=True)
    os.makedirs(export_dir)

    with temp_directory() as cache_dir:
        with settings.temporary():
            settings.set("cache-directory", cache_dir)

            original = fill_cache_with_cds()

            app = CliMetLabApp()
            app.onecmd(f'export_cache --match "era5" {export_dir}')

            exported_files = glob.glob(os.path.join(export_dir, "*"))
            assert len(exported_files) == 2, exported_files

            target = f"{export_dir}/{os.path.basename(original)}"
            assert filecmp.cmp(original, target), (original, target)

    shutil.rmtree(export_dir)


if __name__ == "__main__":
    test_this()
