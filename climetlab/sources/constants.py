# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from ..datasets import load_dataset
from ..sources import load_source
from . import Source
from climetlab.readers.grib.index import FieldSet

LOG = logging.getLogger(__name__)


class Constants(FieldSet):
    def __init__(self, data, names):

        self.data = data
        self.names = names
        self.params = data.unique_values("param")["param"]

    def __len__(self):
        return len(self.data) * len(self.names) // len(self.params)

    def _getitem(self, i):
        return Constant()

    def mutate(self):
        return self


source = Constants
