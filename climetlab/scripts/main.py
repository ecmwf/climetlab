# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import argparse
import cmd
import logging
import os
import sys
import traceback
from importlib import import_module

import entrypoints
from termcolor import colored

from .benchmark import BenchmarkCmd
from .cache import CacheCmd
from .check import CheckCmd
from .grib import GribCmd
from .grib_info import GribInfoCmd
from .settings import SettingsCmd

LOG = logging.getLogger(__name__)

try:
    import readline
except ImportError:  # Not availabe on win32

    class readline:
        def set_history_length(*args, **kwargs):
            pass

        def write_history_file(*args, **kwargs):
            pass

        def read_history_file(*args, **kwargs):
            pass


def get_plugins():
    plugins = []
    for e in entrypoints.get_group_all("climetlab.scripts"):
        module = import_module(e.module_name)
        klass = getattr(module, e.object_name)
        if klass in plugins:
            LOG.error(f"Potential plugins conflict for {module} {klass}.")
            continue
        plugins.append(klass)
    return plugins


class CliMetLabApp(
    cmd.Cmd,
    SettingsCmd,
    CacheCmd,
    CheckCmd,
    GribCmd,
    BenchmarkCmd,
    GribInfoCmd,
    *get_plugins(),
):
    # intro = 'Welcome to climetlab. Type ? to list commands.\n'
    prompt = colored("(climetlab) ", "yellow")

    rc_file = "~/.climetlab-history"

    def postloop(self):
        try:
            readline.set_history_length(1000)
            readline.write_history_file(os.path.expanduser(self.rc_file))
        except Exception:
            pass

    def preloop(self):
        try:
            readline.read_history_file(os.path.expanduser(self.rc_file))
            with open(os.path.expanduser(self.rc_file), "rt") as f:
                for line in f:
                    self.history.append(line[:-1])
        except Exception:
            pass

    def empty_line(self):
        pass

    def do_quit(self, args):
        """Quit climetlab."""
        return True

    def default(self, line):
        if line == "EOF":
            return True

        cmd = colored(line.split()[0], "yellow")
        help = colored("help", "yellow")

        print(
            f"Unknown command {cmd}. Type {help} for the list of known command names."
        )

    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except ValueError as e:
            print(colored(str(e), "red"))
        except Exception:
            traceback.print_exc()
        return False


def main():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument(
        "--debug",
        action="store_true",
        help="verbose operation (default: quiet)",
    )
    p.add_argument(
        "cmdline",
        type=str,
        metavar="CMD",
        nargs=argparse.REMAINDER,
    )

    p.add_argument(
        "-h", "--help", action="store_true", help="show this help message and exit"
    )
    args = p.parse_args()
    if args.help:
        p.print_help()
        cmdline = ["help"]
    else:
        cmdline = args.cmdline

    sys.argv[1:] = cmdline  # TODO: remove this?

    logging.basicConfig(level=args.debug and "DEBUG" or "WARN")

    app = CliMetLabApp()

    if cmdline:
        return app.onecmd(" ".join(cmdline))
    else:
        app.cmdloop()


if __name__ == "__main__":
    main()
