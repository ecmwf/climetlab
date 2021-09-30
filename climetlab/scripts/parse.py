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
from functools import wraps


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(f"{self.prog}: {message}\n\n{self.format_help()}.")


def parse_args(json=False, positional=None):
    def wrapper(func):
        @wraps(func)
        def wrapped(self, args):
            p = ArgumentParser(func.__name__.replace("do_", ""))
            if json:
                p.add_argument(
                    "--json",
                    action="store_true",
                )
            if positional is not None:
                p.add_argument("args", metavar="ARG", type=str, nargs=positional)

            args = p.parse_args(shlex.split(args))

            return func(self, args)

        return wrapped

    return wrapper
