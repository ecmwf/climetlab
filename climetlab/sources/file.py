# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import glob
import logging
import os

from climetlab import load_source
from climetlab.core.settings import SETTINGS
from climetlab.readers import reader

from . import Source

LOG = logging.getLogger(__name__)


class FileSource(Source, os.PathLike):

    _reader_ = None
    path = None
    filter = None
    merger = None

    def mutate(self):

        if isinstance(self.path, (list, tuple)):
            if len(self.path) == 1:
                self.path = self.path[0]
            else:
                return load_source(
                    "multi",
                    [load_source("file", p) for p in self.path],
                    filter=self.filter,
                    merger=self.merger,
                )

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

    def plot_map(self, *args, **kwargs):
        return self._reader.plot_map(*args, **kwargs)

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

    def _attributes(self, names):
        return self._reader._attributes(names)

    def __repr__(self):
        cache_dir = SETTINGS.get("cache-directory")
        if isinstance(self.path, str):
            path = self.path.replace(cache_dir, "CACHE:")
        return f"{self.__class__.__name__}({path},{self._reader.__class__.__name__})"

    def __fspath__(self):
        return self.path


class File(FileSource):
    def __init__(
        self,
        path,
        expand_user=True,
        expand_vars=False,
        unix_glob=True,
        recursive_glob=True,
        filter=None,
        merger=None,
    ):

        if expand_user:
            path = os.path.expanduser(path)

        if expand_vars:
            path = os.path.expandvars(path)

        if unix_glob and set(path).intersection(set("[]?*")):
            matches = glob.glob(path, recursive=recursive_glob)
            if len(matches) == 1:
                path = matches[0]
            if len(matches) > 1:
                path = sorted(matches)

        self.path = path
        self.filter = filter
        self.merger = merger


source = File
