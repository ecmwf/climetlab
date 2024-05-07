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
import sys

import numpy as np
import pytest

from climetlab import load_source
from climetlab import settings
from climetlab.core.caching import purge_cache
from climetlab.core.temporary import temp_directory
from climetlab.mirrors import _reset_mirrors
from climetlab.mirrors import get_active_mirrors
from climetlab.mirrors.directory_mirror import DirectoryMirror
from climetlab.testing import NO_EOD
from climetlab.testing import OfflineError
from climetlab.testing import network_off


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


@pytest.mark.download
def test_mirror_url_source_0(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)
    mirror.activate()

    with pytest.raises(OfflineError):
        load_without_network(force=True)


@pytest.mark.download
def test_mirror_url_source_1(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)
    mirror.activate()

    # load is not enough, as we are not using the cache ()
    load(force=True)
    with pytest.raises(OfflineError):
        load_without_network(force=True)


@pytest.mark.download
def test_mirror_url_source_1bis(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)

    # load is not enough, as we are not using the cache ()
    with mirror:
        load(force=True)
        with pytest.raises(OfflineError):
            load_without_network(force=True)


@pytest.mark.download
def test_mirror_url_source_2(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)
    mirror.activate(prefetch=True)

    # load is enough with prefetch
    load(force=True)
    load_without_network(force=True)


@pytest.mark.download
def test_mirror_url_source_2bis(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)

    # load is enough with prefetch
    with mirror.prefetch():
        load(force=True)

        load_without_network(force=True)


@pytest.mark.download
def test_mirror_url_source_3(mirror_dirs):
    tmpdir, _ = mirror_dirs
    mirror = DirectoryMirror(path=tmpdir)

    with mirror.prefetch():
        load(force=True)

    mirror = DirectoryMirror(path=tmpdir)
    with mirror:
        load_without_network(force=True)


@pytest.mark.download
def test_mirror_url_source_env_var_1(mirror_dirs):
    mirror_dir, _ = mirror_dirs

    origin_prefix = "https://github.com/ecmwf/climetlab/raw/main/docs"
    os.environ["CLIMETLAB_MIRROR"] = f"{origin_prefix} file://{mirror_dir}"

    _reset_mirrors(use_env_var=False)
    assert len(get_active_mirrors()) == 0, get_active_mirrors()

    _reset_mirrors(use_env_var=True)
    assert len(get_active_mirrors()) == 1, get_active_mirrors()


@pytest.mark.skipif(sys.platform == "win32", reason="Cannot unlink tmp directory on Windows")
@pytest.mark.download
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
    assert np.all(source[0].to_numpy() == source2[0].to_numpy()), (source, source2)


@pytest.mark.skip(reason="Multiple mirrors not supported")
@pytest.mark.parametrize("b2", ["__", "b2"])
@pytest.mark.parametrize("a2", ["__", "a2"])
@pytest.mark.parametrize("b1", ["__", "b1"])
@pytest.mark.parametrize("a1", ["__", "a1"])
@pytest.mark.download
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
    force = True

    mirror_a = DirectoryMirror(path=dir1)
    mirror_b = DirectoryMirror(path=dir2)

    def contains(mirror, source):
        path = mirror.contains(source)
        if path:
            assert os.path.exists(path)
        return path

    source = load(force=force)

    if a1:
        with mirror_a.prefetch():
            load(force=force)
    if b1:
        with mirror_b.prefetch():
            load(force=force)

    assert contains(mirror_a, source) == a1, "Prefetching failed for a1"
    assert contains(mirror_b, source) == b1, "Prefetching failed for b1"

    if a2:
        mirror_a.prefetch()
    if b2:
        mirror_b.prefetch()
    with mirror_a:
        with mirror_b:
            assert len(get_active_mirrors()) == 2
            source2 = load(force=force)

    assert contains(mirror_a, source) == (a1 or a2), "Prefetching failed for a"
    assert contains(mirror_b, source) == (b1 or b2), "Prefetching failed for b"

    if a1 or b1 or a2 or b2:
        assert str(source2) == str(source)


def load_eod(**kwargs):
    s = load_source(
        "ecmwf-open-data",
        step=24,
        date=-1,
        stream="enfo",
        type="ef",
        param="2t",
        source="azure",
        number="1",
        **kwargs,
        # force=True,
    )
    print(s)
    print(len(s))
    return s


def load_eod_without_network(**kwargs):
    with network_off():
        return load_eod(**kwargs)


@pytest.mark.skipif(NO_EOD, reason="No access to Open data")
@pytest.mark.download
def test_mirror_eod(mirror_dirs):
    tmpdir, _ = mirror_dirs

    mirror = DirectoryMirror(path=tmpdir)

    with mirror.prefetch():
        source = load_eod()

    purge_cache(matcher=lambda x: not x["path"].endswith(".json"))

    with mirror:
        source2 = load_eod_without_network()

    assert str(source2) == str(source)


if __name__ == "__main__":
    # test_mirror_url_source_1()
    from climetlab.testing import main

    main(__file__)
