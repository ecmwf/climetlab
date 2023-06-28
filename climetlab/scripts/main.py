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

from .availability import AvailabilityCmd
from .benchmark import BenchmarkCmd
from .cache import CacheCmd
from .check import CheckCmd
from .completion import CompletionCmd
from .create import LoadersCmd
from .grib import GribCmd
from .grib_info import GribInfoCmd
from .settings import SettingsCmd
from .test_data import TestDataCmd

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
    CompletionCmd,
    CacheCmd,
    CheckCmd,
    GribCmd,
    BenchmarkCmd,
    GribInfoCmd,
    AvailabilityCmd,
    LoadersCmd,
    TestDataCmd,
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
            lst = line.split()

            def replace_dashes(txt):
                return txt.replace("-", "_")

            if len(lst) == 1:
                line = replace_dashes(lst[0])
            if len(lst) > 1:
                line = " ".join([replace_dashes(lst[0])] + lst[1:])
            return super().onecmd(line)
        except ValueError as e:
            traceback.print_exc()
            print(colored(str(e), "red"))
        except Exception:
            traceback.print_exc()
        return 33


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
    p.add_argument("-v", "--version", action="store_true", help="show version and exit")
    args = p.parse_args()
    if args.version:
        from climetlab import __version__

        print(__version__)
        sys.exit()

    if args.help:
        p.print_help()
        cmdline = ["help"]
    else:
        cmdline = args.cmdline

    sys.argv[1:] = cmdline  # TODO: remove this?

    logging.basicConfig(level=args.debug and "DEBUG" or "WARN")

    app = CliMetLabApp()

    if cmdline:
        res = app.onecmd(" ".join(cmdline))
        if res:
            sys.exit(res)
    else:
        app.cmdloop()


def command_list():
    return [
        func[3:]
        for func in dir(CliMetLabApp)
        if callable(getattr(CliMetLabApp, func))
        and func.startswith("do_")
        and getattr(CliMetLabApp, func).__module__.startswith("climetlab.")
    ]


if __name__ == "__main__":
    main()
