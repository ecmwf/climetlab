# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from climetlab.utils.parts import Parts

from .. import Reader
from .codes import GribFileIndex
from .fieldset import FieldSet

LOG = logging.getLogger(__name__)


class GRIBReader(FieldSet, Reader):
    appendable = True  # GRIB messages can be added to the same file

    def __init__(self, source, path):
        Reader.__init__(self, source, path)

        g = GribFileIndex(path)
        fields = [
            (self.path, offset, length) for offset, length in zip(g.offsets, g.lengths)
        ]

        FieldSet.__init__(self, Parts(fields))

    def __repr__(self):
        return "GRIBReader(%s)" % (self.path,)

    @classmethod
    def merge(cls, readers):

        assert all(isinstance(s, GRIBReader) for s in readers), readers
        assert len(readers) > 1

        fields = []
        for r in readers:
            g = GribFileIndex(r.path)
            fields += [
                (r.path, offset, length) for offset, length in zip(g.offsets, g.lengths)
            ]

        return FieldSet(Parts(fields))
