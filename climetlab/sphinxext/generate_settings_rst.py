#!/usr/bin/env python3
import os
import getpass

from climetlab.core.settings import DEFAULTS

HOME = os.path.expanduser("~/")
USER = getpass.getuser()


def tidy(x):

    if isinstance(x, (list, tuple)):
        return [tidy(y) for y in x]

    if isinstance(x, dict):
        d = {}
        for k, v in x.items():
            d[k] = tidy(v)
        return d

    if isinstance(x, str):
        if x.startswith(HOME):
            n = len(HOME)
            return tidy("~/{}".format(x[n:]))

        if "-" + USER in x:
            return tidy(x.replace("-" + USER, "-${USER}"))

    return x


def execute():

    print()
    print(".. list-table::")
    print("   :header-rows: 1")
    print("   :widths: 70 20 10")
    print()
    print("   * - | Name")
    print("     - | Default")
    print("     - | Description")
    print()
    for k, v in sorted(tidy(DEFAULTS).items()):
        print("   * - |", k)
        print("     - |", v)
        print("     - |", "TODO...")
    print()


if __name__ == "__main__":
    execute()
