#!/usr/bin/env python3
import os
import sys
import yaml
import getpass

top = os.path.realpath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, top)

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
            return tidy("~/{}".format(x[len(HOME) :]))

        if "-" + USER in x:
            return tidy(x.replace("-" + USER, "-${USER}"))


    return x


print()
print(".. code-block:: yaml")
print()
for n in yaml.dump(tidy(DEFAULTS), default_flow_style=False).split("\n"):
    print("   ", n)
print()
