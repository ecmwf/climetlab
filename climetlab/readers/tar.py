# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import tarfile

from .archive import ArchiveReader


class TarReader(ArchiveReader):
    def __init__(self, source, path):
        super().__init__(source, path)

        with tarfile.open(path) as tar:
            self.expand(
                tar,
                tar.getmembers(),
                set_attrs=False,
            )


def _check_tar(path):
    name, ext = os.path.splitext(path)

    if ext in (".tar", ".tgz", ".txz", ".tbz", ".tbz2", ".tb2"):
        return True

    if ext in (".Z", ".gz", ".xz", ".bz2"):
        return name.endswith(".tar")

    return False


def reader(source, path, magic, deeper_check):
    # We don't use tarfile.is_tarfile() because is
    # returns true given a file of zeros
    if _check_tar(path):
        return TarReader(source, path)
