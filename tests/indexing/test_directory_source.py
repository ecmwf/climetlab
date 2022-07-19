import functools
import os

import climetlab as cml
from climetlab import settings
from climetlab.core.temporary import temp_directory

here = os.path.dirname(__file__)


def temp_cache_dir(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        with temp_directory() as tmpdir:
            with settings.temporary():
                settings.set("cache-directory", tmpdir)
                f(*args, **kwargs)

    return wrapped


@temp_cache_dir
def test_db_no_cache():
    s = cml.load_source(
        "directory",
        os.path.join(here, "gribs", "y"),
    )
    print(s, len(s))
    print(s.to_xarray())


@temp_cache_dir
def test_a():
    s = cml.load_source("directory", os.path.join(here, "gribs", "a"), param="t")
    s = cml.load_source(
        "directory", os.path.join(here, "gribs", "a"), param="t", level="1000"
    )
    print(s, len(s))
    ds = s.to_xarray()
    print(ds)


@temp_cache_dir
def test_b():
    s = cml.load_source(
        "directory", os.path.join(here, "gribs", "b"), param="2t", realization="0"
    )
    print(s, len(s))
    ds = s.to_xarray()
    print(ds)


@temp_cache_dir
def test_c():
    with temp_directory() as tmpdir:
        with settings.temporary():
            settings.set("cache-directory", tmpdir)
            s = cml.load_source(
                "directory",
                os.path.join(here, "gribs", "c"),
                param="2t",
                realization="0",
            )
            print(s, len(s))
            ds = s.to_xarray()
            print(ds)


if __name__ == "__main__":
    # test_json_local()
    test_db_no_cache()
    print("--------------")
    # test_db_no_cache()
