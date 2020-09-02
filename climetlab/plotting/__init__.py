# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.helpers import helper
from climetlab.core.ipython import display
from .drivers.magics import Driver
from climetlab.core import docstring
from climetlab.core.data import data_entries


def projections():
    return sorted(e.name for e in data_entries("projections"))


def layers():
    return sorted(e.name for e in data_entries("layers"))


def styles():
    return sorted(e.name for e in data_entries("styles"))


class Plot:
    """[summary]
    """

    def __init__(self, kwargs):
        self.driver = Driver(kwargs)

    def plot_map(self, data=None, **kwargs):

        # try:
        #     iter(data)
        #     data = list(data)
        # except Exception:
        #     pass

        if not isinstance(data, (list, tuple)):
            data = [data]

        for d in data:
            if getattr(d, "plot_map", None) is None:
                d = helper(d)

            d.plot_map(self.driver)

        self.driver.apply_options(kwargs)

    def show(self):
        return display(self.driver.show())

    def macro(self) -> list:
        return self.driver.macro()


def new_plot(**kwargs) -> Plot:
    """[summary]

    :return: [description]
    :rtype: Plot
    """
    return Plot(kwargs)


@docstring()
def plot_map(data=None, **kwargs):
    """Plot any data on a map.

        Args:
            data ([any]): [description]
    """

    p = new_plot(**kwargs)
    p.plot_map(data)
    p.show()


Plot.plot_map.__doc__ = plot_map.__doc__
