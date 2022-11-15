# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from climetlab.readers import Reader
from climetlab.readers.grib.index import FieldSetInOneFile, MultiFieldSet

LOG = logging.getLogger(__name__)


class GRIBReader(FieldSetInOneFile, Reader):
    appendable = True  # GRIB messages can be added to the same file

    def __init__(self, source, path):
        Reader.__init__(self, source, path)
        FieldSetInOneFile.__init__(self, path)

    def __repr__(self):
        return "GRIBReader(%s)" % (self.path,)

    @classmethod
    def merge(cls, readers):

        assert all(isinstance(s, GRIBReader) for s in readers), readers
        assert len(readers) > 1

        return MultiFieldSet(readers)

    def index_content(self):
        assert False, "not used"
        from climetlab.readers.grib.parsing import _index_grib_file

        yield from _index_grib_file(self.path)
