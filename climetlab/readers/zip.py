# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
from zipfile import ZipFile

from . import Reader


class ZIPReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

        with ZipFile(path, "r") as z:
            self._content = z.namelist()

        if len(self._content) != 1:
            raise NotImplementedError("Multi-file zip not yet supported")

    def to_pandas(self, **kwargs):

        _, ext = os.path.splitext(self._content[0])
        if ext not in (".csv", ".txt"):
            raise NotImplementedError("File type", ext)

        import pandas

        options = dict(compression="zip")
        options.update(self.source.read_csv_options())
        options.update(kwargs)

        return pandas.read_csv(self.path, **options)
