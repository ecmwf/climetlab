# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import tarfile

from .archive import ArchiveReader


class TarReader(ArchiveReader):
    def __init__(self, source, path):
        super().__init__(source, path)

        with tarfile.open(path) as tar:
            self._content = tar.getmembers()

        self.expand(
            tar.getmembers(),
            set_attrs=False,
        )

    def open(self, path):
        return tarfile.open(path)


def reader(source, path, magic, deeper_check):

    # Only check during the second pass as tarfile.is_tarfile()
    # is potentially slow on large files
    if deeper_check:
        if tarfile.is_tarfile(path):
            return TarReader(source, path)
