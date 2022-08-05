import glob
import os
import shutil

import climetlab as cml
from climetlab import settings
from climetlab.core.temporary import temp_directory
from climetlab.scripts.main import CliMetLabApp

def test_this():
    directory = 'tata'
    shutil.rmtree(directory, ignore_errors=True)

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

            s = cml.load_source("directory", directory)
            assert len(s) == len(s1) + len(s2), (len(s1), len(s2), len(s))
            db_path = os.path.abspath(os.path.join(directory, "climetlab.db"))
            assert s.index.db.db_path == db_path

            assert s.to_numpy().mean() == 277.31256510416665
            print('finishing settings.temporary()')
            print('finishing settings.temporary()')
        print('finishing tmp cache_dir')
        print('finishing tmp cache_dir')
    print('finishing')
    print('finishing')
    
if __name__ == "__main__":
    test_this()
