# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import glob
import logging
import os
import time

import pyfdb

from climetlab.readers.grib.index import GribDBIndex
from climetlab.utils.parts import Part

LOG = logging.getLogger(__name__)


class FDB(GribDBIndex):
    def __init__(self, root=None, schema=None, request={}):
        super().__init__(db=None)

        if root:
            os.environ["FDB_ROOT_DIRECTORY"] = root

        if schema is None and root is not None:
            for n in glob.iglob(f"{root}/*/schema"):
                schema = n
                break

        if schema:
            os.environ["FDB_SCHEMA_FILE"] = schema

        now = time.time()
        self.parts = list(pyfdb.list(request))
        print("pyfdb.list", time.time() - now)

    def number_of_parts(self):
        return len(self.parts)

    def part(self, i):
        f = self.parts[i]
        return Part(f["path"], f["offset"], f["length"])


source = FDB
