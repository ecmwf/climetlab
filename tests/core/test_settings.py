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
import yaml

import climetlab.plotting
from climetlab import settings
from climetlab.core.data import clear_cache
from climetlab.core.data import get_data_entry
from climetlab.core.plugins import directories
from climetlab.core.temporary import temp_directory


def check_user_defined_objects(collection, setting, obj, tree, get_list, get_entry):
    # Clear cache
    clear_cache()

    paths = settings.get(setting)
    assert isinstance(paths, (list, tuple)), paths
    assert len(paths) > 0

    for i, path in enumerate(paths):
        name = "pytest-%s-%s" % (tree[1], i)

        if os.path.exists(path) and os.path.isdir(path):
            assert path in directories(), directories()

        if not os.path.exists(path):
            os.mkdir(path)

        with open(os.path.join(path, "%s.yaml" % (name,)), "w") as f:
            a = obj
            for t in tree[:-1]:
                a = a[t]
            a[tree[-1]] = i
            yaml.dump(obj, f, default_flow_style=False)

    for i in range(len(paths)):
        name = "pytest-%s-%s" % (tree[1], i)
        get_data_entry(collection, name)
        assert name in get_list()
        p = get_entry(name).data

        a = p
        for t in tree:
            a = a[t]

        assert a == i

    # TODO: Move to tear-down
    for i, path in enumerate(paths):
        name = "pytest-%s-%s" % (tree[1], i)
        os.unlink(os.path.join(path, "%s.yaml" % (name,)))


def test_user_projections():
    check_user_defined_objects(
        "projections",
        "projections-directories",
        {"magics": {"mmap": {}}},
        ["magics", "mmap", "subpage_lower_left_latitude"],
        climetlab.plotting.projections,
        climetlab.plotting.projection,
    )


def test_user_styles_msymb():
    check_user_defined_objects(
        "styles",
        "styles-directories",
        {"magics": {"msymb": {}}},
        ["magics", "msymb", "symbol_marker_index"],
        climetlab.plotting.styles,
        climetlab.plotting.style,
    )


def test_user_styles_mcont():
    check_user_defined_objects(
        "styles",
        "styles-directories",
        {"magics": {"mcont": {}}},
        ["magics", "mcont", "contour_line_thickness"],
        climetlab.plotting.styles,
        climetlab.plotting.style,
    )


def test_user_layers():
    check_user_defined_objects(
        "layers",
        "layers-directories",
        {"magics": {"mcoast": {}}},
        ["magics", "mcoast", "map_grid_frame_thickness"],
        climetlab.plotting.layers,
        climetlab.plotting.layer,
    )


def test_settings():
    with settings.temporary():
        settings.reset()

        assert settings.get("plotting-options") == {}, "Check 1"
        settings.set("plotting-options", width=400)
        assert settings.get("plotting-options") == {"width": 400}
        settings.reset("plotting-options")
        assert settings.get("plotting-options") == {}, "Check 2"
        settings.set("plotting-options", {"width": 400})
        assert settings.get("plotting-options") == {"width": 400}
        settings.reset()
        assert settings.get("plotting-options") == {}, "Check 3"

        with pytest.raises(TypeError):
            settings.set("plotting-options", 3)

        settings.set("styles-directories", ["/a", "/b"])
        assert settings.get("styles-directories") == ["/a", "/b"]

        settings.set("styles-directories", "/c", "/d")
        assert settings.get("styles-directories") == ["/c", "/d"]

        with pytest.raises(KeyError):
            settings.set("test", 42)

        with pytest.raises(KeyError):
            settings.get("test")

        with pytest.raises(ValueError):
            settings.set("url-download-timeout", "1M")


def test_temporary():
    settings.reset()

    settings.set("styles-directories", "/c", "/d")
    settings.set("plotting-options", {"width": 400})

    with settings.temporary("plotting-options", {"width": 100}):
        assert settings.get("styles-directories") == ["/c", "/d"]
        assert settings.get("plotting-options") == {"width": 100}, settings.get("plotting-options")
        settings.set("plotting-options", {"width": 200})
        assert settings.get("plotting-options") == {"width": 200}
        settings.reset()
        assert settings.get("plotting-options") == {}

    settings.set("plotting-options", {"width": 400})
    settings.set("styles-directories", "/c", "/d")

    settings.reset()
    assert settings.get("plotting-options") == {}


def test_numbers():
    with temp_directory() as tmpdir:
        with settings.temporary("cache-directory", tmpdir):
            settings.set("url-download-timeout", 30)
            assert settings.get("url-download-timeout") == 30

            settings.set("url-download-timeout", "30")
            assert settings.get("url-download-timeout") == 30

            settings.set("url-download-timeout", "30s")
            assert settings.get("url-download-timeout") == 30

            settings.set("url-download-timeout", "2m")
            assert settings.get("url-download-timeout") == 120

            settings.set("url-download-timeout", "10h")
            assert settings.get("url-download-timeout") == 36000

            settings.set("url-download-timeout", "7d")
            assert settings.get("url-download-timeout") == 7 * 24 * 3600

            with pytest.raises(ValueError):
                settings.set("url-download-timeout", "1x")

            settings.set("maximum-cache-size", "1")
            assert settings.get("maximum-cache-size") == 1

            settings.set("maximum-cache-size", "1k")
            assert settings.get("maximum-cache-size") == 1024

            settings.set("maximum-cache-size", "1kb")
            assert settings.get("maximum-cache-size") == 1024

            settings.set("maximum-cache-size", "1k")
            assert settings.get("maximum-cache-size") == 1024

            settings.set("maximum-cache-size", "1kb")
            assert settings.get("maximum-cache-size") == 1024

            settings.set("maximum-cache-size", "1K")
            assert settings.get("maximum-cache-size") == 1024

            settings.set("maximum-cache-size", "1M")
            assert settings.get("maximum-cache-size") == 1024 * 1024

            settings.set("maximum-cache-size", "1G")
            assert settings.get("maximum-cache-size") == 1024 * 1024 * 1024

            settings.set("maximum-cache-size", "1T")
            assert settings.get("maximum-cache-size") == 1024 * 1024 * 1024 * 1024

            settings.set("maximum-cache-size", "1P")
            assert settings.get("maximum-cache-size") == 1024 * 1024 * 1024 * 1024 * 1024

            settings.set("maximum-cache-size", None)
            assert settings.get("maximum-cache-size") is None

            settings.set("maximum-cache-disk-usage", "2%")
            assert settings.get("maximum-cache-disk-usage") == 2


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
