# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import copy

# import atexit
import datetime
import json
import logging
import os
import warnings

import eccodes

from climetlab import load_source
from climetlab.core import Base
from climetlab.core.caching import auxiliary_cache_file
from climetlab.profiling import call_counter

# from climetlab.decorators import dict_args
from climetlab.utils.bbox import BoundingBox

from .. import Reader
from .fieldset import FieldSet

# from collections import defaultdict


LOG = logging.getLogger(__name__)


class GRIBReader(FieldSet, Reader):
    appendable = True  # GRIB messages can be added to the same file

    def __init__(self, source, path):
        Reader.__init__(self, source, path)
        FieldSet.__init__(self, paths=[path])

    def __repr__(self):
        return "GRIBReader(%s)" % (self.path,)

    @classmethod
    def merge(cls, readers):
        from climetlab.mergers import merge_by_class

        assert all(isinstance(s, GRIBReader) for s in readers), readers
        assert len(readers) > 1

        return FieldSet(paths=[r.path for r in readers])
