# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging
import os

from climetlab.readers.grib.index import SqlIndex
from climetlab.scripts.grib import _index_grib_file
from climetlab.sources.indexed import IndexedSource

LOG = logging.getLogger(__name__)


def make_absolute(filename, root_dir, default):
    if filename is None:
        filename = default

    if os.path.isabs(filename):
        return filename

    return os.path.join(root_dir, filename)


class DirectorySource(IndexedSource):
    DEFAULT_JSON_FILE = "climetlab.index"
    DEFAULT_DB_FILE = "climetlab.db"

    def __init__(self, path, index_file=None, _index=None, **kwargs):
        """index_file is the input index location. db_path is the actual used index.
        index_file = None,  db_path = None :  parse file to create the index.
        index_file = xxx ,  db_path = None :  create db_path in the cache from index_file if not exist
        index_file = xxx ,  db_path = yyy  :  create db_path in "db_path" from index_file if not exist
        """
        if _index is not None:  # for .sel()
            super().__init__(_index, **kwargs)
            return

        self.path = path
        self.abspath = os.path.abspath(path)

        db_path = "climetlab.db"
        db_path = make_absolute(
            db_path,
            self.abspath,
            default=self.DEFAULT_DB_FILE,
        )

        # Try to use db_path if it exists:
        if db_path is not None and os.path.exists(db_path):
            LOG.info(f"Using index file {db_path}")
            index = SqlIndex.from_db_path(db_path=db_path)
            super().__init__(index, **kwargs)
            return

        index_file = make_absolute(
            index_file,
            self.abspath,
            default=self.DEFAULT_JSON_FILE,
        )
        assert db_path != index_file

        # Try to use index_file (json) if it exists:
        if os.path.exists(index_file):
            LOG.info(f"Using index file {index_file}")
            index = SqlIndex.from_file(
                path=index_file,
                db_path=db_path,
            )
            super().__init__(index, **kwargs)
            return

        # Create the db_path file (or use the one in cache)
        LOG.info(f"Did not find index files in {db_path} or {index_file}")
        index = SqlIndex.from_scanner(
            self._parse_files(path, ignore=db_path),
            db_path=db_path,
            cache_metadata={"directory": self.path},
        )
        super().__init__(index, **kwargs)

    def sel(self, **kwargs):
        return self.__class__(self, _index=self.index.sel(**kwargs))

    def _parse_files(self, path, ignore=None):
        ignore = ["climetlab.index"]
        if ignore:
            ignore.append(ignore)
        ignore.append(self.DEFAULT_DB_FILE)
        ignore.append(self.DEFAULT_JSON_FILE)

        LOG.debug(f"Parsing files in {path}")
        assert os.path.isdir(path)
        for root, _, files in os.walk(path):
            for name in files:
                if name in ignore:
                    continue
                relpath = os.path.join(root, name)
                p = os.path.abspath(relpath)
                LOG.debug(f"Parsing file in {p}")
                yield from _index_grib_file(p)  # , path_name=relpath)


source = DirectorySource
