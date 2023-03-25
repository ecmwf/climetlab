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

show_stack = '--stack' in sys.argv
show_first = '--first' in sys.argv


class SpecFinder:
    def find_spec(self, name, path=None, target=None):
        if show_first:
            for f in inspect.stack():
                if f.filename == __file__:
                    continue

                if "importlib._bootstrap" in f.filename:
                    continue

                print('=', name, f.filename, f.lineno)
                return

        print('=', name)
        if show_stack:
            for f in inspect.stack():
                if f.filename == __file__:
                    continue

                if "importlib._bootstrap" in f.filename:
                    continue

                print("    ", f.filename, f.lineno)


sys.meta_path.insert(0, SpecFinder())


import climetlab as cml # noqa

# This should trigger a lot of wrappers
cml.load_source('file', __file__)
