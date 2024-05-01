# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import argparse
import functools
import shlex
import textwrap
from itertools import cycle

from termcolor import colored


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(f"{self.prog}: {message}\n\n{self.format_help()}.")


def parse_args(epilog="", **kwargs):
    def wrapper(func):
        doc = "" if func.__doc__ is None else func.__doc__

        p = ArgumentParser(
            func.__name__.replace("do_", ""),
            description=textwrap.dedent(doc),
            epilog=textwrap.dedent(epilog),
            add_help=False,
        )
        # custom help to avoid exiting from climetlab cli.
        p.add_argument(
            "-h", "--help", action="store_true", help="show this help message and exit"
        )

        for k, v in kwargs.items():
            k = k.replace("_", "-")

            if isinstance(v, dict):  # short form is handled directly
                p.add_argument(f"--{k}", **v)
                continue

            assert isinstance(v, (list, tuple)), v
            lst, dic = v[:-1], v[-1]
            assert isinstance(dic, dict), dic
            lst = list(lst)
            if len(lst) == 0:
                lst = [k]
            if lst[0] is None:
                lst[0] = k
            if not lst[0] in [k, f"--{k}"]:
                lst = [f"--{k}"] + lst

            p.add_argument(*lst, **dic)

        func._argparser = p
        func._kwargs_specifications = kwargs

        @functools.wraps(func)
        def wrapped(self, args):
            args = shlex.split(args)  # shlex honors the quotes
            args = p.parse_args(args)
            if args.help:
                p.print_help()
                return
            return func(self, args)

        return wrapped

    return wrapper


def experimental(func):
    func._climetlab_experimental = True
    return func


def print_table(rows, colours=["blue"]):
    rows = list(rows)
    colours = list(colours)
    width = max(len(x[0]) for x in rows)
    for row, colour in zip(rows, cycle(colours)):
        print("{0:<{width}} {1}".format(row[0], colored(row[1], colour), width=width))
