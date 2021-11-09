# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import warnings

from climetlab.decorators import normalize


class normalize_args:
    def __init__(self, **dic):
        warnings.warn(
            "Deprecated decorator @normalize_arg. Use @normalise on each argument instead."
        )
        self.decorators = []
        for name, values in dic.items():

            if isinstance(values, list):
                self.decorators.append(normalize(name, values, multiple=True))
                continue

            if isinstance(values, tuple):
                warnings.warn(
                    "Using tuple to set multiple=False is deprecated in @normalize_arg. Use with multiple=False."
                )
                self.decorators.append(normalize(name, values, multiple=False))
                continue

            self.decorators.append(normalize(name, values))

    def __call__(self, func):
        for d in self.decorators:
            func = d(func)
        return func
