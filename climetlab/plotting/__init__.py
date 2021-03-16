# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.core import docstring
from climetlab.core.data import data_entries, get_data_entry
from climetlab.core.ipython import display
from climetlab.core.settings import SETTINGS
from climetlab.helpers import helper

from .drivers.magics.driver import Driver
from .options import Options

OPTIONS = {}


def options(**kwargs):
    global OPTIONS
    OPTIONS = kwargs


def projection(name):
    return get_data_entry("projections", name)


def layer(name):
    return get_data_entry("layers", name)


def style(name):
    return get_data_entry("styles", name)


def projections():
    return sorted(e.name for e in data_entries("projections"))


def layers():
    return sorted(e.name for e in data_entries("layers"))


def styles():
    return sorted(e.name for e in data_entries("styles"))


class Plot:
    """[summary]"""

    def __init__(self, kwargs):
        options = {}
        options.update(SETTINGS.get("plotting-options", {}))
        options.update(OPTIONS)
        options.update(kwargs)
        self.driver = Driver(Options(options))

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

        options = Options(kwargs)
        self.driver.apply_options(options)
        options.check_unused()

        return self

    def wms_layers(self):
        return self.driver.wms_layers()

    def show(self):
        return display(self.driver.show())

    def macro(self) -> list:
        return self.driver.macro()

    def save(self, path):
        return self.driver.save(path)


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


def interactive_map(data=None, **kwargs):
    from climetlab.plotting.wms import interactive_map as wms_map

    return wms_map(data, **kwargs)
