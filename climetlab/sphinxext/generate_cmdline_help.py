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


def iprint(*args, indent=2):
    print(" " * indent, end="")
    print(*args)


def print_rst_underline(txt, padding="-", indent=0):
    iprint(txt, indent=indent)


def execute(*args):

    cmd_list = [(cmd, getattr(CliMetLabApp, cmd)) for cmd in dir(CliMetLabApp)]
    cmd_list = [(cmd, func) for (cmd, func) in cmd_list if cmd.startswith("do_")]
    cmd_list = [(cmd, func) for (cmd, func) in cmd_list if hasattr(func, "_argparser")]
    cmd_list = [(cmd[3:], func) for (cmd, func) in cmd_list]  # remove "do_"
    cmd_list = sorted(cmd_list, key=lambda x: x[0])

    assert len(cmd_list) > 0, "Documentation for climetlab CLI is empty"

    for cmd, func in cmd_list:
        module = func.__module__.split(".")[0]

        print()
        print("--------------------")
        print()
        print(f".. _{cmd}-command:")
        print()
        title = cmd
        if module != "climetlab":
            title = title + f"[{module}]"
        if getattr(func, "_climetlab_experimental", False):
            title = title + " (experimental)"
        print(title)
        print("-" * len(title))
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
                n = "climetlab " + n[7:]
                print("Usage")
                print('"""""')
                iprint()
                iprint(".. code-block:: text")
                iprint()
                iprint(" ", n)
                continue

            if len(n.strip()) == 0:
                iprint()
                iprint()
                continue

            if n.endswith(" arguments:"):
                n = n[:-1]  # remove trailing ":"
                print(n[0].upper() + n[1:])
                print('"' * len(n))
                iprint()
                iprint(".. code-block:: text")
                iprint()
                continue

            if n.lower().startswith("examples:"):
                n = n[9:]
                print("Examples")
                print('""""""""')
                iprint()
                iprint(".. code-block:: text")
                iprint()
                iprint(" ", n)
                continue

            if n.strip().startswith("-"):
                iprint(" ", n)
                continue

            iprint(n)


if __name__ == "__main__":
    execute()
