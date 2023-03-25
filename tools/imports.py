#!/usr/bin/env python3
# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import inspect
import sys

show_stack = "--stack" in sys.argv
show_first = "--first" in sys.argv
show_fail_if_loaded = "--fail" in sys.argv


def call_stack():
    for f in inspect.stack():
        if f.filename == __file__:
            continue

        if "importlib._bootstrap" in f.filename:
            continue

        yield (f.filename, f.lineno)


class SpecFinder:
    def find_spec(self, name, path=None, target=None):
        if show_fail_if_loaded:
            if name in sys.argv[1:]:
                filename = "?"
                lineno = 0
                for filename, lineno in call_stack():
                    break
                print(f"{name} loaded from {filename}:{lineno}")
                sys.exit(1)
            return
        if show_first:
            for filename, lineno in call_stack():
                print("=", name, f"{filename}:{lineno}")
                return

        print("=", name)
        if show_stack:
            for filename, lineno in call_stack():
                print(
                    f"    {filename}:{lineno}",
                )


sys.meta_path.insert(0, SpecFinder())


import climetlab as cml  # noqa

# This should trigger a lot of wrappers
cml.load_source("file", __file__)
