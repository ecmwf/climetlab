# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import metview as mv

from climetlab.core.ipython import ipython_active

if ipython_active:
    try:
        import ipywidgets  # noqa

        mv.setoutput("jupyter", plot_widget=True)
    except ImportError:
        mv.setoutput("jupyter", plot_widget=False)


def mv_read(*args, **kwargs):
    return mv.read(*args, **kwargs)


def mv_read_table(*args, **kwargs):
    return mv.read_table(*args, **kwargs)
