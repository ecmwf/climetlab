# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import warnings
from importlib import import_module


class Helper:
    pass


_HELPERS = {}


# TODO: Add plugins
# TODO: Add lock
def _helpers():
    if not _HELPERS:
        here = os.path.dirname(__file__)
        for path in os.listdir(here):
            if path.endswith(".py") and path[0] not in ("_", "."):
                name, _ = os.path.splitext(path)
                try:
                    _HELPERS[name] = import_module(f".{name}", package=__name__).helper
                except Exception as e:
                    warnings.warn(f"Error loading helper {name}: {e}")
    return _HELPERS


def helper(data, *args, **kwargs):
    """
    Returns an object that wraps classes from other packages
    to support
    """

    if hasattr(data, "helper"):
        return data.helper(*args, **kwargs)

    for name, h in _helpers().items():
        try:
            helper = h(data, *args, **kwargs)
            if helper is not None:
                return helper
        except Exception as e:
            warnings.warn(f"Error calling helper {name}: {e}")

    fullname = ".".join([data.__class__.__module__, data.__class__.__qualname__])

    raise ValueError(f"Cannot find a helper for class {fullname}")
