# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

"""
ipython is not None when running a notebook
"""

import logging
import sys

from ..utils import module_loaded

ipython_active = None
if module_loaded("IPython"):
    try:
        from IPython import get_ipython

        ipython_active = get_ipython()
    except Exception:
        pass

"""

Run that code in a cell:

from climetlab.core.ipython import ipython_environment
ipython_environment()

"""


def guess_which_ipython():
    if ipython_active is None:
        return (None, None)

    if ipython_active.ipython_dir == "/deepnote-config/ipython":
        return ("deepnote", None)

    if "google.colab" in repr(ipython_active.inspector):
        return ("colab", None)

    if "IPython.terminal" in repr(ipython_active.parent):
        return ("ipython", None)

    if ipython_active.__class__.__name__ == "ZMQInteractiveShell":
        return ("jupyter-lab", None)

    if isinstance(
        ipython_active.python_dir, str
    ) and ipython_active.python_dir.endswith(".ipython"):
        return ("jupyter-lab", None)
    return ("unknown", None)


def tidy(x):
    if x is None:
        return x

    if isinstance(x, (list, tuple)):
        return [tidy(y) for y in x]

    if isinstance(x, dict):
        r = {}
        for k, v in x.items():
            r[str(k)] = tidy(v)
        return r

    if isinstance(x, (int, float, str)):
        return x

    import re

    return re.sub(r" object at x\w+", repr(x), "")


def ipython_environment():
    import json

    import IPython

    r = {}
    k = IPython.get_ipython()
    for n in dir(k):
        if not callable(getattr(k, n)) and not n.startswith("__"):
            r[n] = getattr(k, n)
    print(json.dumps(tidy(r), sort_keys=True, indent=4))


def enable_ipython_logging(level=logging.INFO):
    class Filter(logging.Filter):
        def filter(self, message):
            return message.levelno < logging.WARNING

    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)

    stdout = logging.StreamHandler(sys.stdout)
    stdout.setLevel(level)
    stdout.addFilter(Filter())
    logger.addHandler(stdout)

    stderr = logging.StreamHandler(sys.stderr)
    stderr.setLevel(logging.WARNING)
    logger.addHandler(stderr)


def _identity(x, **kwargs):
    return x


if ipython_active:
    from IPython.display import HTML
    from IPython.display import SVG as SVG_ipython
    from IPython.display import Image, Markdown, display

    def SVG(*args, **kwargs):
        import IPython

        ipython_major = int(IPython.__version__.split(".")[0])

        if ipython_major < 6 and "metadata" in kwargs:
            kwargs.pop("metadata")

        return SVG_ipython(*args, **kwargs)

    # enable_ipython_logging()
else:
    Image = _identity
    SVG = _identity
    HTML = _identity
    Markdown = _identity
    display = _identity

__all__ = ["display", "Image", "SVG", "HTML", "Markdown"]
