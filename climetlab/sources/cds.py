# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import cdsapi
import os

from .base import FileSource
from climetlab.core.caching import temp_file


class CDSRetriever(FileSource):

    def __init__(self, dataset, **req):
        self.path = temp_file('CDSRetriever', req)
        if not os.path.exists(self.path):
            cdsapi.Client().retrieve(dataset, req, self.path + '.tmp')
            os.rename(self.path + '.tmp', self.path)


source = CDSRetriever
