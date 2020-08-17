# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from importlib import import_module

HELPERS = {
    "xarray.core.dataset.Dataset": "xarray",
    "xarray.core.dataarray.DataArray": "xarray",
    "numpy.ndarray": "ndarray",
    "pandas.core.frame.DataFrame": "pandas",
    "builtins.NoneType": "none",
}


def helper(data, *args, **kwargs):
    """
    Returns an object that wraps classes from other packages
    to support
    """

    fullname = ".".join([data.__class__.__module__, data.__class__.__qualname__])

    name = HELPERS.get(fullname)

    if name is not None:
        helper = import_module(".%s" % (name,), package=__name__)
        return helper.helper(data, *args, **kwargs)

    raise ValueError("Cannot find a helper for class %s" % (fullname,))
