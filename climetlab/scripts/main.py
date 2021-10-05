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

from termcolor import colored

from .cache import CacheCmd
from .check import CheckCmd
from .settings import SettingsCmd

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


class ClimetlabApp(
    cmd.Cmd,
    SettingsCmd,
    CacheCmd,
    CheckCmd,
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
    p = argparse.ArgumentParser()
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
    args = p.parse_args()
    sys.argv[1:] = cmdline = args.cmdline

    logging.basicConfig(level=args.debug and "DEBUG" or "WARN")

    app = ClimetlabApp()

    if cmdline:
        return app.onecmd(" ".join(cmdline))
    else:
        app.cmdloop()


if __name__ == "__main__":
    main()