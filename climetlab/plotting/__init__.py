# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

# This is needed when running Sphinx on ReadTheDoc
try:
    from .drivers.magics import Driver

except Exception:
    from .drivers.missing import Driver

from importlib import import_module

try:
    from IPython.display import display
except Exception:

    def display(x):
        return x


CURRENT_DRIVER = Driver()

HELPERS = {
    "xarray.core.dataset.Dataset": "xarray",
    "xarray.core.dataarray.DataArray": "xarray",
    "numpy.ndarray": "ndarray",
    "pandas.core.frame.DataFrame": "pandas",
}


def plot_map(data, *args, **kwargs):
    # This is a standalone plot, so we reset the driver
    CURRENT_DRIVER = Driver(*args, **kwargs)
    if getattr(data, "plot_map", None) is None:

        fullname = ".".join([data.__class__.__module__, data.__class__.__qualname__])

        name = HELPERS.get(fullname)

        if name is not None:
            helper = import_module(".helpers.%s" % (name,), package=__name__)
            data = helper.helper(data, *args, **kwargs)
        else:
            raise ValueError("Cannot plot %s" % (fullname,))

    data.plot_map(CURRENT_DRIVER)

    return display(CURRENT_DRIVER.show(**kwargs))
