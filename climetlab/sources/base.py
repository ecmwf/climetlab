# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from . import DataSource
from .readers import reader


class FileSource(DataSource):

    _reader_ = None

    @property
    def _reader(self):
        if self._reader_ is None:
            self._reader_ = reader(self.path)
        return self._reader_

    def __iter__(self):
        return iter(self._reader)

    def __len__(self):
        return len(self._reader)

    def __getitem__(self, n):
        return self._reader[n]

    def to_xarray(self, *args, **kwargs):
        return self._reader.to_xarray(*args, **kwargs)

    def to_pandas(self, *args, **kwargs):
        return self._reader.to_pandas(*args, **kwargs)

    def to_numpy(self, *args, **kwargs):
        return self._reader.to_numpy(*args, **kwargs)

    def to_metview(self, *args, **kwargs):
        return self._reader.to_metview(*args, **kwargs)
