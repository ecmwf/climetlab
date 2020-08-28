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

active = None
try:
    from IPython import get_ipython

    active = get_ipython()
except Exception:
    pass


def _identity(x, **kwargs):
    return x


if active:
    from IPython.display import display, Image, SVG, HTML, Markdown
else:
    Image = _identity
    SVG = _identity
    HTML = _identity
    Markdown = _identity
    display = _identity

__all__ = ["display", "Image", "SVG", "HTML", "Markdown"]
