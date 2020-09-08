# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# Keep linters happy
# N801 = classes should start with uppercase


class docstring:  # noqa: N801
    def __init__(self):
        pass

    def __call__(self, func):
        # func.__doc__ += "Decorated...."
        return func
