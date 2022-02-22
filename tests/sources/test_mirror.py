#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import os

import pytest

from climetlab import load_source, settings
from climetlab.core.temporary import temp_directory
from climetlab.mirrors import _reset_mirrors, get_mirrors
from climetlab.mirrors.directory_mirror import DirectoryMirror
from climetlab.testing import IN_GITHUB, OfflineError, network_off


def load(**kwargs):
    source = load_source(
        "url",
        "https://github.com/ecmwf/climetlab/raw/main/docs/examples/test.grib",
        **kwargs,
    )
    assert len(source) == 2, source
    return source


def load_without_network(**kwargs):
    with network_off():
        return load(**kwargs)


@pytest.fixture()
def mirror_dirs():
    """Setup for mirror tests:
    - a temporary cache dir,
    - temporary settings,
    - two temporary directories
    """
    with temp_directory() as cachedir:
        with settings.temporary():
            settings.set("cache-directory", cachedir)
            with temp_directory() as mirrordir:
                with temp_directory() as mirrordir2:
                    _reset_mirrors(use_env_var=False)
                    yield mirrordir, mirrordir2


def test_mirror_url_source_0(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)
    mirror.activate()

    with pytest.raises(OfflineError):
        load_without_network(force=True)


def test_mirror_url_source_1(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)
    mirror.activate()

    # load is not enough, as we are not using the cache ()
    load(force=True)
    with pytest.raises(OfflineError):
        load_without_network(force=True)


def test_mirror_url_source_1bis(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)

    # load is not enough, as we are not using the cache ()
    with mirror:
        load(force=True)
        with pytest.raises(OfflineError):
            load_without_network(force=True)


def test_mirror_url_source_2(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)
    mirror.activate(prefetch=True)

    # load is enough with prefetch
    load(force=True)
    load_without_network(force=True)


def test_mirror_url_source_2bis(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)

    # load is enough with prefetch
    with mirror.prefetch():
        load(force=True)

        load_without_network(force=True)


def test_mirror_url_source_3(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)

    with mirror.prefetch():
        load(force=True)

    mirror = DirectoryMirror(path=tmpdir)
    with mirror:
        load_without_network(force=True)


def test_mirror_url_source_env_var_1(mirror_dirs):
    mirror_dir, _ = mirror_dirs

    origin_prefix = "https://github.com/ecmwf/climetlab/raw/main/docs"
    os.environ["CLIMETLAB_MIRROR"] = f"{origin_prefix} file://{mirror_dir}"

    _reset_mirrors(use_env_var=False)
    assert len(get_mirrors()) == 0, get_mirrors()

    _reset_mirrors(use_env_var=True)
    assert len(get_mirrors()) == 1, get_mirrors()


def test_mirror_url_source_env_var_2(mirror_dirs):
    mirror_dir, _ = mirror_dirs
    source = load(force=True)

    os.makedirs(f"{mirror_dir}/url/examples", exist_ok=True)
    source.save(f"{mirror_dir}/url/examples/test.grib")

    origin_prefix = "https://github.com/ecmwf/climetlab/raw/main/docs"
    os.environ["CLIMETLAB_MIRROR"] = f"{origin_prefix} file://{mirror_dir}"

    m = DirectoryMirror(path=mirror_dir, origin_prefix=origin_prefix)
    with m:
        source2 = load_without_network(force=True)

    assert source.connect_to_mirror(m, {}).contains()

    assert str(source) == f"Url({origin_prefix}/examples/test.grib)"
    if not IN_GITHUB:
        assert str(source2) == f"Url(file://{mirror_dir}/url/examples/test.grib)"


@pytest.mark.skipif(True, reason="Not implemented yet")
@pytest.mark.parametrize("b2", ["__", "b2"])
@pytest.mark.parametrize("a2", ["__", "a2"])
@pytest.mark.parametrize("b1", ["__", "b1"])
@pytest.mark.parametrize("a1", ["__", "a1"])
def test_mirror_url_source_multiple_copy(
    mirror_dirs,
    a1,
    b1,
    a2,
    b2,
):
    dir1, dir2 = mirror_dirs
    a1 = a1 == "a1"
    b1 = b1 == "b1"
    a2 = a2 == "a2"
    b2 = b2 == "b2"

    mirror1 = DirectoryMirror(path=dir1)
    mirror2 = DirectoryMirror(path=dir2)

    source = load(force=True)

    if a1:
        with mirror1.prefetch():
            load(force=True)
    if b1:
        with mirror2.prefetch():
            load(force=True)

    assert mirror1.contains(source, {}) == a1, "Prefetching failed for a2"
    assert mirror2.contains(source, {}) == b1, "Prefetching failed for b2"

    if a2:
        mirror1.prefetch()
    if b2:
        mirror2.prefetch()
    with mirror1:
        with mirror2:
            assert len(get_mirrors()) == 2
            source2 = load(force=True)

    assert mirror1.contains(source, {}) == (a2 or a1), f"mirror 1: a2={a2} or a1={a1}"
    assert mirror2.contains(source, {}) == (b2 or b1), f"mirror 2: b2={b2} or b1={b1}"
    if a1 or b1 or a2 or b2:
        assert str(source2) != str(source)


if __name__ == "__main__":
    # test_mirror_url_source_1()
    from climetlab.testing import main

    main(__file__)
