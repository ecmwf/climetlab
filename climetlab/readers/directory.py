# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import fnmatch
import logging
import os
import shutil

from climetlab import load_source

from . import Reader
from . import reader as find_reader

LOG = logging.getLogger(__name__)


class GlobFilter:
    def __init__(self, pattern, top):
        self.pattern = pattern
        self.skip = len(top) + 1

    def __call__(self, path):
        match = fnmatch.fnmatch(path[self.skip :], self.pattern)
        LOG.debug("GlobFilter %s %s %s", path[self.skip :], self.pattern, match)
        return match


def make_file_filter(filter, top):
    if filter is None:
        return lambda _: True

    if callable(filter):
        return filter

    if isinstance(filter, str):
        return GlobFilter(filter, top)

    raise TypeError(f"Invalid filter {filter}")


class DirectoryReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

        self._content = []

        filter = make_file_filter(self.filter, self.path)

        for root, _, files in os.walk(self.path):
            for file in files:
                full = os.path.join(root, file)
                LOG.debug("%s", full)
                if filter(full):
                    self._content.append(full)

    def mutate(self):
        if len(self._content) == 1:
            return find_reader(self.source, self._content[0])
        return self

    def mutate_source(self):
        if os.path.exists(os.path.join(self.path, ".zattrs")):
            return load_source("zarr", self.path)

        return load_source(
            "multi",
            [
                load_source(
                    "file",
                    path=path,
                    filter=self.filter,
                    merger=self.merger,
                )
                for path in sorted(self._content)
            ],
            filter=self.filter,
            merger=self.merger,
        )

    def save(self, path):
        shutil.copytree(self.path, path)

    def write(self, f):
        raise NotImplementedError()


def reader(source, path, magic=None, deeper_check=False):
    if magic is None or os.path.isdir(path):
        return DirectoryReader(source, path)
