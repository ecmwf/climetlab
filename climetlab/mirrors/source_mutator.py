# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import climetlab as cml


class SourceMutator:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def mutate_source(self):
        return cml.load_source(*self.args, **self.kwargs)
