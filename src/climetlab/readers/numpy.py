# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

import numpy as np

from . import Reader


class NumpyReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

    def to_numpy(self, numpy_load_kwargs={}):
        return np.load(self.path, **numpy_load_kwargs)

    def __iter__(self):
        return iter([self])


class NumpyZipReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

    def to_numpy(self, numpy_load_kwargs={}):
        return np.load(self.path, **numpy_load_kwargs)


def reader(source, path, magic=None, deeper_check=False):
    if magic is None:  # Bypass check and force
        return NumpyReader(source, path)

    if magic[:6] == b"\x93NUMPY":
        return NumpyReader(source, path)

    _, extension = os.path.splitext(path)
    if magic[:4] == b"PK\x03\x04" and extension == ".npz":
        return NumpyZipReader(source, path)
