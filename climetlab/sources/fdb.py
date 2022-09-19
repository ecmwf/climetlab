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
import yaml

from climetlab.readers.grib.index import FieldSetInFiles
from climetlab.utils.parts import Part

LOG = logging.getLogger(__name__)


class FDB(FieldSetInFiles):
    def __init__(self, root=None, schema=None, request={}):
        super().__init__(db=None)

        if schema is None and root is not None:
            for n in glob.iglob(f"{root}/*/schema"):
                schema = n
                break

        config = {
            "spaces": [{"roots": [{"path": root}]}],
            "schema": schema,
        }
        os.environ["FDB5_CONFIG"] = yaml.dump(config)

        now = time.time()

        fdb = pyfdb.FDB()
        self.parts = list(fdb.list(request))
        print("pyfdb.list", time.time() - now)

    def number_of_parts(self):
        return len(self.parts)

    def part(self, i):
        f = self.parts[i]
        return Part(f["path"], f["offset"], f["length"])


source = FDB
