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

ipython_active = None
try:
    from IPython import get_ipython

    ipython_active = get_ipython()
except Exception:
    pass


def enable_ipython_login(level=logging.INFO):
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
    from IPython.display import display, Image, SVG, HTML, Markdown

    # enable_ipython_login()
else:
    Image = _identity
    SVG = _identity
    HTML = _identity
    Markdown = _identity
    display = _identity

__all__ = ["display", "Image", "SVG", "HTML", "Markdown"]
