# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import stat
from zipfile import ZipFile

from climetlab import load_source

from .archive import ArchiveReader
from .csv import CSVReader


class InfoWrapper:
    """
    A class so that ZipInfo has the same interface as TarInfo
    """

    def __init__(self, member):
        self.member = member
        self.file_or_directory = True
        # See https://stackoverflow.com/questions/35782941/archiving-symlinks-with-python-zipfile
        if member.create_system == 3:  # Unix
            unix_mode = member.external_attr >> 16
            self.file_or_directory = stat.S_ISDIR(unix_mode) or stat.S_ISREG(unix_mode)

    @property
    def name(self):
        return self.member.filename

    def isdir(self):
        return self.file_or_directory and self.member.filename.endswith("/")

    def isfile(self):
        return self.file_or_directory and not self.isdir()


class ZIPReader(ArchiveReader):
    def __init__(self, source, path):
        super().__init__(source, path)

        with ZipFile(path, "r") as z:
            self._content = z.infolist()

        if len(self._content) == 1:
            _, ext = os.path.splitext(self._content[0].filename)
            if ext in (".csv", ".txt"):
                return  # Pandas can read zipped files directly

        if ".zattrs" in self._content:
            return  # Zarr can read zipped files directly

        self.expand(self._content)

    def open(self, path):
        return ZipFile(path, "r")

    def check(self, member):
        return super().check(InfoWrapper(member))

    def mutate(self):

        if not os.path.isdir(self.path) and len(self._content) == 1:
            _, ext = os.path.splitext(self._content[0].filename)
            if ext not in (".csv", ".txt"):
                raise NotImplementedError("File type", ext)
            return CSVReader(self.source, self.path, compression="zip").mutate()

        return super().mutate()

    def mutate_source(self):
        # zarr can read data from a zip file
        if ".zattrs" in self._content:
            return load_source("zarr", self.path)

        return None


EXTENSIONS_TO_SKIP = (".npz",)  # Numpy arrays


def reader(source, path, magic, deeper_check):
    _, extension = os.path.splitext(path)

    if magic[:4] == b"PK\x03\x04" and extension not in EXTENSIONS_TO_SKIP:
        return ZIPReader(source, path)
