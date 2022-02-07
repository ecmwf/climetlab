# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import argparse
import shlex
import textwrap
from functools import wraps
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
        )

        for k, v in kwargs.items():
            if "nargs" in v:
                p.add_argument(k, **v)
            else:
                p.add_argument(f"--{k}", **v)

        func._argparser = p

        @wraps(func)
        def wrapped(self, args):
            args = p.parse_args(shlex.split(args))
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
