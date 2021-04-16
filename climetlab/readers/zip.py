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
from . import reader as find_reader


class ZIPReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

        with ZipFile(path, "r") as z:
            self._content = z.namelist()

        if len(self._content) == 1:
            _, ext = os.path.splitext(self._content[0])
            if ext in (".csv", ".txt"):
                return  # Pandas can read zipped files directly

        extract_path = self.source.cache_file(path, extension=".d")
        if not os.path.exists(extract_path):
            tmp = extract_path + ".tmp"
            with ZipFile(path, "r") as z:
                z.extractall(tmp)
            os.rename(tmp, extract_path)

        self.path = extract_path

    def mutate(self):
        if os.path.isdir(self.path):
            return find_reader(self.source, self.path)
        return self

    def to_pandas(self, **kwargs):

        _, ext = os.path.splitext(self._content[0])
        if ext not in (".csv", ".txt"):
            raise NotImplementedError("File type", ext)

        import pandas

        options = dict(compression="zip")
        options.update(self.source.read_csv_options())
        options.update(kwargs)

        return pandas.read_csv(self.path, **options)


def reader(source, path, magic):
    if magic[:4] == b"PK\x03\x04":
        return ZIPReader(source, path)
