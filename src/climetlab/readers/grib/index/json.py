# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from climetlab.decorators import cached_method
from climetlab.indexing.database.json import JsonFileDatabase
from climetlab.readers.grib.index.db import FieldsetInFilesWithDBIndex


class FieldsetInFilesWithJsonIndex(FieldsetInFilesWithDBIndex):
    DBCLASS = JsonFileDatabase

    @cached_method
    def _lookup_parts(self):
        return self.db.lookup_parts()

    def part(self, n):
        return self._lookup_parts()[n]

    def number_of_parts(self):
        return len(self._lookup_parts())
