# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os

import pyfdb

from climetlab.readers.grib.index import GribIndexFromFile
from climetlab.utils.parts import Part

LOG = logging.getLogger(__name__)


class NoLock:
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass


class FDB(GribIndexFromFile):
    def __init__(self, root=None, schema=None, request={}):
        super().__init__(db=None)
        if root:
            os.environ["FDB_ROOT_DIRECTORY"] = root
        if schema:
            os.environ["FDB_SCHEMA_FILE"] = schema

        self.fields = list(pyfdb.list(request))

    def number_of_parts(self):
        return len(self.fields)

    def part(self, i):
        f = self.fields[i]
        return Part(f["path"], f["offset"], f["length"])


source = FDB
