# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

from climetlab import load_source

from . import Reader


class DirectoryReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

        self._content = []

        for root, _, files in os.walk(path):
            for file in files:
                self._content.append(os.path.join(root, file))

        assert self._content, path

    def mutate(self):
        sources = [load_source("file", path) for path in self._content]
        return load_source("multi", sources).mutate()


def reader(source, path, magic):
    if os.path.isdir(path):
        return DirectoryReader(source, path)
