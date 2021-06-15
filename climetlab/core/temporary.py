# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import tempfile


class TmpFile:
    """The TmpFile objets are designed to be used for temporary files.
    It ensures that the file is unlinked when the object is
    out-of-scope (with __del__).

    Parameters
    ----------
    path : str
        Actual path of the file.
    """

    def __init__(self, path: str):
        self.path = path

    def __del__(self):
        os.unlink(self.path)


def temp_file(extension=".tmp") -> TmpFile:
    """Create a temporary file with the given extension .

    Parameters
    ----------
    extension : str, optional
        By default ".tmp"

    Returns
    -------
    TmpFile
    """

    fd, path = tempfile.mkstemp(suffix=extension)
    os.close(fd)
    return TmpFile(path)
