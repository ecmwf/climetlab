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

# This is needed when running Sphinx on ReadTheDoc
try:
    from .drivers.magics import Driver

except Exception:
    from .drivers.missing import Driver


def plot_map(data, **kwargs):
    """Foo bar

    Args:
        data (str): Kdd

    Returns:
        str: path
    """

    driver = Driver(kwargs)

    if not isinstance(data, (list, tuple)):
        data = [data]

    for d in data:
        if getattr(d, "plot_map", None) is None:
            d = helper(d)

        d.plot_map(driver)

    return display(driver.show())


class Plot:
    """[summary]
    """
    def __init__(self, kwargs):
        self.driver = Driver(kwargs)

    def plot_map(self, data, **kwargs):
        if not isinstance(data, (list, tuple)):
            data = [data]

        for d in data:
            if getattr(d, "plot_map", None) is None:
                d = helper(d)

        d.plot_map(self.driver)
        self.driver.apply_options(kwargs)

    def show(self):
        return display(self.driver.show())

    def macro(self):
        return self.driver.macro()


def new_plot(**kwargs):
    """[summary]

    :return: [description]
    :rtype: [type]
    """
    return Plot(kwargs)
