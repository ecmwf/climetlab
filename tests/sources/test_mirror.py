#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import pytest

from climetlab import load_source, settings
from climetlab.core.temporary import temp_directory
from climetlab.testing import OfflineError, network_off
from climetlab.utils.mirror import UrlMirror, prefetch


def load(**kwargs):
    return load_source(
        "url",
        "https://github.com/ecmwf/climetlab/raw/main/docs/examples/test.grib",
        force=True,
        **kwargs,
    )


def load_without_network(**kwargs):
    with network_off():
        load(**kwargs)


def test_mirror_url_source_1():
    with temp_directory() as cachedir, settings.temporary():
        settings.set("cache-directory", cachedir)
        with temp_directory() as tmpdir:
            mirror = UrlMirror({"https://": f"file://{tmpdir}/"})

            with pytest.raises(OfflineError):
                load_without_network(mirror=mirror)

            # load is not enough, as we are not using the cache (force=True)
            load()

            with pytest.raises(OfflineError):
                load_without_network(mirror=mirror)

            # building the mirror
            with prefetch(tmpdir):
                load()

            load_without_network(mirror=mirror)


def test_mirror_url_source_2():
    with temp_directory() as cachedir, settings.temporary():
        settings.set("cache-directory", cachedir)
        with temp_directory() as tmpdir:
            mirror = UrlMirror({"https://": f"file://{tmpdir}/"})

            with pytest.raises(OfflineError):
                load_without_network(mirror=mirror)

            load()

            with pytest.raises(OfflineError):
                load_without_network(mirror=mirror)

            load(build_mirror=mirror)

            load_without_network(mirror=mirror)


if __name__ == "__main__":
    # test_mirror_url_source_1()
    from climetlab.testing import main

    main(__file__)
