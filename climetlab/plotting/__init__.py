# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.core.data import data_entries, get_data_entry
from climetlab.core.ipython import display
from climetlab.core.settings import SETTINGS
from climetlab.wrappers import get_wrapper

from .options import Options

OPTIONS = {}


def magics(*args, **kwargs):
    from .backends.magics.backend import Backend as MagicsBackend

    return MagicsBackend(*args, **kwargs)


def bokeh(*args, **kwargs):
    from .backends.bokeh.backend import Backend as BokehBackend

    return BokehBackend(*args, **kwargs)


def matplotlib(*args, **kwargs):
    from .backends.matplotlib.backend import Backend as MatplotlibBackend

    return MatplotlibBackend(*args, **kwargs)


DRIVERS = {
    None: magics,
    "magics": magics,
    "matplotlib": matplotlib,
    "bokeh": bokeh,
}


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
        backend = SETTINGS.get(f"{self.kind}-plotting-backend", None)
        backend = kwargs.pop("backend", backend)

        options = {}
        options.update(SETTINGS.get("plotting-options", {}))
        options.update(OPTIONS)
        options.update(kwargs)
        self.backend = DRIVERS[backend](Options(options))

    def plot_graph(self, data=None, **kwargs):

        if not isinstance(data, (list, tuple)):
            data = [data]

        for d in data:
            d = get_wrapper(d)
            d.plot_graph(self.backend)

        options = Options(kwargs)
        self.backend.apply_options(options)
        options.check_unused()

        return self

    def plot_map(self, data=None, **kwargs):

        if not isinstance(data, (list, tuple)):
            data = [data]

        for d in data:
            d = get_wrapper(d)
            d.plot_map(self.backend)

        options = Options(kwargs)
        self.backend.apply_options(options)
        options.check_unused()

        return self

    def wms_layers(self):
        return self.backend.wms_layers()

    def render(self):
        return self.backend.render()

    def show(self):
        self.backend.show(display=display)

    def macro(self) -> list:
        return self.backend.macro()

    def save(self, path):
        return self.backend.save(path)


class MapPlot(Plot):
    kind = "map"


class GraphPlot(Plot):
    kind = "graph"


def new_plot(**kwargs) -> Plot:
    """[summary]

    :return: [description]
    :rtype: Plot
    """
    return MapPlot(kwargs)


def new_graph(**kwargs) -> Plot:
    """[summary]

    :return: [description]
    :rtype: Plot
    """
    return GraphPlot(kwargs)


def plot_graph(data=None, **kwargs):
    """Plot other-than-map data

    Args:
        data ([any]): [description]
    """

    p = new_graph(**kwargs)
    p.plot_graph(data)
    p.show()


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


def new_table(*args, **kwargs):
    from climetlab.notebook.table import Table

    return Table(*args, **kwargs)
