# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from .database import SqlDatabase


class IndexBackend:
    pass


class JsonIndexBackend(IndexBackend):
    def __init__(self, url):
        self.db = SqlDatabase(url=url)

    def lookup(self, request):
        return self.db.lookup(request)
