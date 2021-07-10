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
from . import reader as find_reader


class DirectoryReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

        self._content = []

        filter = self.filter

        for root, _, files in os.walk(path):
            for file in files:
                full = os.path.join(root, file)
                if filter(full):
                    self._content.append(full)

    def mutate(self):
        if len(self._content) == 1:
            return find_reader(self.source, self._content[0])
        return self

    def mutate_source(self):
        if os.path.exists(os.path.join(self.path, ".zattrs")):
            return load_source("zarr", self.path)

        return load_source(
            "multi",
            [
                load_source(
                    "file",
                    c,
                    self.filter,
                    self.merger,
                )
                for c in self._content
            ],
        )


def reader(source, path, magic):
    if os.path.isdir(path):
        return DirectoryReader(source, path)
