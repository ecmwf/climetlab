# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.


import logging

from . import Reader

LOG = logging.getLogger(__name__)


class Unknown(Reader):
    def __init__(self, source, path, magic):
        super().__init__(source, path)
        self.magic = magic
        LOG.warning("Unknown file type %s (%s), ignoring", path, magic)

    def ignore(self):
        # Used by multi-source
        return True

    def __len__(self):
        return 0
