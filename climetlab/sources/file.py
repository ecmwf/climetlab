# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging

from climetlab.core.settings import SETTINGS
from climetlab.readers import reader

from . import Source

LOG = logging.getLogger(__name__)


class FileSource(Source):

    _reader_ = None
    path = None
    filter = None
    merger = None

    def mutate(self):
        # Give a chance to directories and zip files
        # to return a multi-source
        source = self._reader.mutate_source()
        if source not in (None, self):
            source._parent = self
            return source
        return self

    def ignore(self):
        return self._reader.ignore()

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

    def sel(self, **kwargs):
        return self._reader.sel(**kwargs)

    def plot_map(self, **kwargs):
        return self._reader.plot_map(**kwargs)

    def to_xarray(self, **kwargs):
        return self._reader.to_xarray(**kwargs)

    def to_tfdataset(self, **kwargs):
        return self._reader.to_tfdataset(**kwargs)

    def to_pandas(self, **kwargs):
        LOG.debug("Calling reader.to_pandas %s", self)
        return self._reader.to_pandas(**kwargs)

    def to_numpy(self, **kwargs):
        return self._reader.to_numpy(**kwargs)

    def to_metview(self, **kwargs):
        return self._reader.to_metview(**kwargs)

    def save(self, path):
        return self._reader.save(path)

    def write(self, f):
        return self._reader.write(f)

    @classmethod
    def multi_merge(cls, sources):
        if not all(isinstance(s, FileSource) for s in sources):
            return None
        readers = [s._reader for s in sources]
        return readers[0].multi_merge(readers)

    def _attributes(self, names):
        return self._reader._attributes(names)

    def __repr__(self):
        cache_dir = SETTINGS.get("cache-directory")
        path = self.path.replace(cache_dir, "CACHE:")
        return f"{self.__class__.__name__}({path},{self._reader.__class__.__name__})"


class File(FileSource):
    def __init__(self, path, filter=None, merger=None):
        self.path = path
        self.filter = filter
        self.merger = merger


source = File
