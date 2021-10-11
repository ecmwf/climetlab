#!/usr/bin/env python3
# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import argparse

from climetlab.scripts.main import CliMetLabApp


def execute(*args):

    for cmd in sorted([c for c in dir(CliMetLabApp) if c.startswith("do_")]):
        func = getattr(CliMetLabApp, cmd)
        if not hasattr(func, "_argparser"):
            continue

        cmd = cmd[3:]  # remove "do_"

        print()
        print(f".. _{cmd}-command:")
        print()
        print(cmd)
        print("^" * len(cmd))
        print()

        # Not garanteed to work with future versions of Python
        func._argparser.formatter_class = (
            lambda prog: argparse.RawDescriptionHelpFormatter(
                prog,
                width=90,
                max_help_position=10000,
            )
        )

        for n in func._argparser.format_help().split("\n"):

            if n.startswith("usage: "):
                print()
                print(".. code-block:: text")
                print()
                print(" ", n)
                continue

            if len(n.strip()) == 0:
                print()
                print()
                continue

            if n.endswith(" arguments:"):
                print(n[0].upper() + n[1:])
                print('"' * len(n))
                print()
                print(".. code-block:: text")
                print()
                continue

            if n.strip().startswith("-"):
                print(" ", n)
                continue

            print(n)


if __name__ == "__main__":
    execute()
