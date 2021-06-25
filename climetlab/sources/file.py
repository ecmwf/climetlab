# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

from climetlab.readers import reader

from . import Source


class FileSource(Source):

    _reader_ = None
    path = None

    def mutate(self):
        # Give a chance to directories and zip files
        # to return a multi-source
        source = self._reader.mutate_source()
        if source not in (None, self):
            source._parent = self
            return source
        return self

    @property
    def _reader(self):
        if self._reader_ is None:
            self._reader_ = reader(self, self.path)
        return self._reader_

    def __iter__(self):
        return iter(self._reader)

    def __len__(self):
        return len(self._reader)

    def __getitem__(self, n):
        return self._reader[n]

    def sel(self, *args, **kwargs):
        return self._reader.sel(*args, **kwargs)

    def plot_map(self, *args, **kwargs):
        return self._reader.plot_map(*args, **kwargs)

    def to_xarray(self, *args, **kwargs):
        return self._reader.to_xarray(*args, **kwargs)

    def to_tfrecord(self, *args, **kwargs):
        return self._reader.to_tfrecord(*args, **kwargs)

    def to_pandas(self, *args, **kwargs):
        return self._reader.to_pandas(*args, **kwargs)

    def to_numpy(self, *args, **kwargs):
        return self._reader.to_numpy(*args, **kwargs)

    def to_metview(self, *args, **kwargs):
        return self._reader.to_metview(*args, **kwargs)

    @classmethod
    def multi_merge(cls, sources):
        if not all(isinstance(s, FileSource) for s in sources):
            return None
        readers = [s._reader for s in sources]
        return readers[0].multi_merge(readers)

    def _attributes(self, names):
        return self._reader._attributes(names)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.path},{self._reader.__class__.__name__})'


class File(FileSource):
    def __init__(self, path):
        self.path = path

    def read_csv_options(self):
        return {}


source = File
