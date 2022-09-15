# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

LOG = logging.getLogger(__name__)


class Database:
    def lookup_parts(self):
        raise NotImplementedError("")

    def lookup_dicts(self):
        raise NotImplementedError("")

    def count(self, request):
        raise NotImplementedError("")

    def load(self, iterator):
        raise NotImplementedError("")

    def sel(self, selection):
        raise NotImplementedError("")

    def order_by(self, order):
        raise NotImplementedError("")
