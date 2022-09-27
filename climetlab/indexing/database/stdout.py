# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import logging

from . import Database

LOG = logging.getLogger(__name__)


class StdoutDatabase(Database):
    def __init__(self, db_path):
        pass

    def load(self, iterator):
        count = 0
        for entry in iterator:
            count += 1
            print(json.dumps(entry))
        return count
