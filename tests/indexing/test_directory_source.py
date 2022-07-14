import os

import pytest

import climetlab as cml
from climetlab import settings
from climetlab.core.temporary import temp_directory

here = os.path.dirname(__file__)


def temp_cache_dir(f):
    def wrapped(*args, **kwargs):
        with temp_directory() as tmpdir:
            with settings.temporary():
                settings.set("cache-directory", tmpdir)
                f(*args, **kwargs)

    return wrapped


@pytest.mark.parametrize("index_type", ["sql", "json"])
def test_directory_with_local_index_file(index_type):
    temp_cache_dir(_test_directory)(index_type, True)


@pytest.mark.parametrize("index_type", ["sql", "json"])
def test_directory_with_cached_index_file(index_type):
    temp_cache_dir(_test_directory)(index_type, False)


def _test_directory(index_type, cache):
    s = cml.load_source(
        "directory",
        os.path.join(here, "gribs", "y"),
        index_type=index_type,
        index_next_to_data=cache,
    )
    print(s, len(s))
    print(s.to_xarray())


@temp_cache_dir
def test_db_with_cache():
    s = cml.load_source(
        "directory",
        os.path.join(here, "gribs", "y"),
        index_type="json",
        index_next_to_data=False,
    )
    print(s, len(s))
    print(s.to_xarray())


@temp_cache_dir
def test_db_no_cache():
    s = cml.load_source(
        "directory",
        os.path.join(here, "gribs", "y"),
        index_type="json",
        index_next_to_data=True,
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
    test_db_with_cache()
    print("--------------")
    # test_db_no_cache()
