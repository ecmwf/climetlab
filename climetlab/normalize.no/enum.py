# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


class EnumNormaliser:
    def __init__(self, values=tuple()):
        self.values = values

    def normalise(self, value):
        for n in self.values:
            if value.lower() == n.lower():
                return n
        raise ValueError(value)
