# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import argparse
import json
import logging
import os
import readline
import sys
from importlib import import_module

import cmd2
from termcolor import colored

import climetlab

settings_parser = cmd2.Cmd2ArgumentParser()
settings_parser.add_argument("words", nargs="*")


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
        except Exception:
            pass

    def empty_line(self):
        pass

    @cmd2.with_argparser(settings_parser)
    def do_settings(self, args):
        print(args.words)
        from climetlab import settings

        if len(args.words) == 0:
            settings.dump()
            return

        if len(args.words) == 1:
            name = args.words[0]
            print(settings.get(name))
            return

        if len(args.words) == 2:
            name = args.words[0]
            value = args.words[1]
            settings.set(name, value)

    def do_cache(self, args):
        from climetlab.core.caching import dump_cache_database

        for i in dump_cache_database():
            print(json.dumps(i, sort_keys=True, indent=4))

    def do_decache(self, args):
        from climetlab.core.caching import purge_cache

        purge_cache()

    def do_check(self, args):
        print(
            (
                "This script is experimental to help debugging."
                "Seeing everything to 'ok' does NOT means that you have the right versions installed."
            )
        )
        print("--------------------")

        print("Checking climetlab installation.")
        print(f"Climetlab installed in {os.path.dirname(climetlab.__file__)}")
        print("Checking required compiled dependencies...")

        import ecmwflibs

        versions = ecmwflibs.versions()

        for name in ["eccodes", "magics"]:
            try:
                print(
                    f"  {name} from ecwmlibs: ok {versions[name]} ({ecmwflibs.find(name)})"
                )
            except Exception as e:  # noqa: F841
                print(f"  {name} from ecmwflib: Warning: ecmwflibs cannot find {name}")

        for name in ["eccodes", "MagPlus", "netcdf"]:
            try:
                import findlibs
            except Exception as e:  # noqa: F841
                print(f"    {name} from findlibs: Warning: cannot import findlibs")
                continue
            try:
                print(f"    {name} from findlibs: ({findlibs.find(name)})")
            except Exception as e:  # noqa: F841
                print(f"    {name} from findlibs: Warning: findlibs cannot find {name}")

        print("Checking required python dependencies...")
        for name in ["xarray", "Magics", "eccodes", "ecmwflibs"]:
            more = ""
            try:
                lib = import_module(name)
            except ImportError:
                print(f"  Error: cannot import {name}.")
                continue
            if name == "eccodes":
                more = f" (using .lib={lib.lib})"
            print(
                f"  {name}: ok {lib.__version__} ({os.path.dirname(lib.__file__)}){more}"
            )

        print("Checking optional dependencies...")
        for name in ["folium", "pdbufr", "pyodc"]:
            try:
                lib = import_module(name)
                print(
                    f"  {name}: ok {lib.__version__} ({os.path.dirname(lib.__file__)})"
                )
            except Exception as e:
                print(e)
                print(f"  Warning: cannot import {name}. Limited capabilities.")

        # TODO: add more
        # TODO: automate this from requirements.txt. Create a pip install climetlab[extra] or climetlab-light.


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--debug", action="store_true", help="verbose operation (default: quiet)"
    )
    p.add_argument("cmdline", type=str, metavar="CMD", nargs=argparse.REMAINDER)
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
