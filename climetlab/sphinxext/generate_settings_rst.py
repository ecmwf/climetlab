import os
import sys
import yaml
import getpass

from ..core.settings import DEFAULTS

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


def execute(out):
    save = sys.stdout
    sys.stdout = out
    try:
        print()
        print(".. code-block:: yaml")
        print()
        for n in yaml.dump(tidy(DEFAULTS), default_flow_style=False).split("\n"):
            print("   ", n)
        print()
    finally:
        sys.stdout = save
