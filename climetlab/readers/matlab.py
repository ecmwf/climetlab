# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from . import Reader


class MatlabReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

    def to_numpy(self, key=None, scipy_io_loadmat_kwargs={}):
        from scipy.io import loadmat

        ds = loadmat(self.path, **scipy_io_loadmat_kwargs)
        if key is not None:
            ds = ds[key]
        return ds

    def __iter__(self):
        return iter([self])


def reader(source, path, magic=None, deeper_check=False):
    if magic[:7] == b"MATLAB ":
        return MatlabReader(source, path)
