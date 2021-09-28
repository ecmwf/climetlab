# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import sys
from importlib import import_module

import climetlab
import cmd2
import argparse
import logging
from termcolor import colored
import readline

class ClimetlabApp(cmd2.Cmd):
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
        except Exception as e:
            pass

    def empty_line(self):
        pass

    def do_decache(self, args):
        print("decache")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--debug", action="store_true",
                   help="verbose operation (default: quiet)")
    p.add_argument("cmdline", type=str, metavar="CMD",
                   nargs=argparse.REMAINDER)
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
