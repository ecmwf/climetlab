# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from climetlab.sources.file import FileSource

LOG = logging.getLogger(__name__)


class Metview(FileSource):
    def __init__(self, metview_object):
        super().__init__(path=metview_object.url())


source = Metview
