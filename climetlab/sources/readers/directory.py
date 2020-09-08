# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

from . import Reader, reader


class DirectoryReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

        self._content = []

        for root, _, files in os.walk(path):
            for file in files:
                self._content.append(os.path.join(root, file))

    def mutate(self):
        # If there is only one file, let's mutate to the proper reader

        if len(self._content) == 1:
            return reader(self.source, self._content[0])

        return self

    def to_xarray(self):
        import xarray as xr

        return xr.open_mfdataset(self._content, combine="by_coords")
