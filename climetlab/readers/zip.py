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

from climetlab import load_source

from . import Reader
from . import reader as find_reader
from .csv import CSVReader

try:
    import ipywidgets  # noqa
    from tqdm.auto import tqdm
except ImportError:
    from tqdm import tqdm


class ZIPReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

        with ZipFile(path, "r") as z:
            self._content = z.namelist()

        if len(self._content) == 1:
            _, ext = os.path.splitext(self._content[0])
            if ext in (".csv", ".txt"):
                return  # Pandas can read zipped files directly

        if ".zattrs" in self._content:
            return  # Zarr can read zipped files directly

        def unzip(target, args):
            with ZipFile(path, "r") as z:
                files = z.namelist()
                for file in tqdm(iterable=files, total=len(files)):
                    z.extract(member=file, path=target)

        self.path = self.cache_file(
            unzip,
            path,
            extension=".d",
            replace=path,
        )

    def mutate(self):
        if os.path.isdir(self.path):
            return find_reader(self.source, self.path).mutate()

        if len(self._content) == 1:
            _, ext = os.path.splitext(self._content[0])
            if ext not in (".csv", ".txt"):
                raise NotImplementedError("File type", ext)
            return CSVReader(self.source, self.path, compression="zip").mutate()

        return self

    def mutate_source(self):
        if ".zattrs" in self._content:
            return load_source("zarr", self.path)

        return None


EXTENSIONS_TO_SKIP = (".npz",)  # Numpy arrays


def reader(source, path, magic):
    _, extension = os.path.splitext(path)

    if magic[:4] == b"PK\x03\x04" and extension not in EXTENSIONS_TO_SKIP:
        return ZIPReader(source, path)
