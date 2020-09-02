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
import climetlab
from importlib import import_module
import sys

CACHE = {}

PLUGINS = {}


def _load_plugins(kind):
    plugins = {}
    for e in entrypoints.get_group_all(f"climetlab.{kind}s"):
        plugins[e.name.replace("_", "-")] = e
    return plugins


def load_plugins(kind):
    if PLUGINS.get(kind) is None:
        PLUGINS[kind] = _load_plugins(kind)
    return PLUGINS[kind]


def find_plugin(directory, name, loader):

    plugins = load_plugins(loader.kind)

    if name in plugins:
        plugin = plugins[name]
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


def directories():
    result = [os.path.dirname(climetlab.__file__)]
    for kind in ("dataset", "source"):
        for _, v in load_plugins(kind).items():
            try:
                module = import_module(v.module_name)
                result.append(os.path.dirname(module.__file__))
            except Exception as e:
                print("Cannot load module", v.module_name, e, file=sys.stderr)
    return result
