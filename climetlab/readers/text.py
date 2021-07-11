# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

from . import Reader


class TextReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

    def ignore(self):
        # Used by multi-source
        return True


def reader(source, path, magic, deeper_check):
    _, extension = os.path.splitext(path)
    if extension in (".txt",):
        return TextReader(source, path)
