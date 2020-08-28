# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import entrypoints

CACHE = {}

PLUGINS = {}


def _load_plugins(kind):
    plugins = {}
    for e in entrypoints.get_group_all(f"climetlab.{kind}s"):
        plugins[e.name.replace("_", "-")] = e
    return plugins


def find_plugin(directory, name, loader):

    kind = loader.kind

    if PLUGINS.get(kind) is None:
        PLUGINS[kind] = _load_plugins(kind)

    if name in PLUGINS[kind]:
        plugin = PLUGINS[kind][name]
        return loader.load_entry(plugin)

    n = len(directory)
    for path, _, files in os.walk(directory):
        path = path[n:]
        for f in files:
            if f.endswith(".yaml"):
                if f[:-5] == name:
                    full = os.path.join(directory, path, f)
                    return loader.load_yaml(full)

            if f.endswith(".py"):
                p = os.path.join(path, f[:-3])
                if p[0] != "/":
                    p = "/" + p
                if p[1:].replace("/", "-").replace("_", "-") == name:
                    return loader.load_module(p.replace("/", "."))

    raise Exception("Cannot find %s '%s'" % (kind, name))
