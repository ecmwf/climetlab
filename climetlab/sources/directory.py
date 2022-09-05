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
from climetlab.readers.grib.parsing import GribIndexingDirectoryParserIterator
from climetlab.sources.indexed import IndexedSource

LOG = logging.getLogger(__name__)


def make_absolute(filename, root_dir, default):
    if filename is None:
        filename = default

    if os.path.isabs(filename):
        return filename

    absolute = os.path.join(root_dir, filename)
    LOG.debug(f"Transforming {filename} into absolute path {absolute}")
    return absolute


class DirectorySource(IndexedSource):
    DEFAULT_JSON_FILE = "climetlab.index"
    DEFAULT_DB_FILE = "climetlab.db"

    def __init__(
        self,
        path,
        db_path=None,
        index_file=None,
        _index=None,
        **kwargs,
    ):
        """index_file is the input index location. db_path is the actual used index.
        index_file = None,  db_path = None :  parse file to create the index.
        index_file = xxx ,  db_path = None :  create db_path in the cache from index_file if not exist
        index_file = xxx ,  db_path = yyy  :  create db_path in "db_path" from index_file if not exist

        if _index is not None, ignore all other arguments.
        """
        self._availability = None

        if _index is not None:  # for .sel()
            super().__init__(_index, **kwargs)
            return

        path = os.path.expanduser(path)

        self.path = path
        self.abspath = os.path.abspath(path)

        if db_path is None:
            db_path = make_absolute(
                db_path,
                self.abspath,
                default=self.DEFAULT_DB_FILE,
            )

        # Try to use db_path if it exists:
        if os.path.exists(db_path):
            LOG.info(f"Using index file {db_path}")
            index = SqlIndex.from_existing_db(db_path=db_path)
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
            print(f"Using index file {index_file} (will happen only once).")
            index = SqlIndex.from_file(path=index_file)
            super().__init__(index, **kwargs)
            return

        # Create the db_path file in cache (or used the cached one)
        LOG.info(f"Did not find index files in {db_path} or {index_file}")
        ignore = [self.DEFAULT_DB_FILE, self.DEFAULT_JSON_FILE, db_path, index_file]
        index = SqlIndex.from_iterator(
            GribIndexingDirectoryParserIterator(
                path, ignore=ignore, relative_paths=False
            ),
            cache_metadata={"directory": self.path},
        )
        super().__init__(index, **kwargs)

    def sel(self, **kwargs):
        # TODO: move this to mother class
        kwargs = self.alias_arguments(**kwargs)
        return self.__class__(self, _index=self.index.sel(**kwargs))

    def order_by(self, arg=None, **kwargs):
        # TODO: move this to mother class
        kwargs = self.alias_arguments(**kwargs)
        order = dict()
        if arg:
            arg = self.alias_arguments(**arg)
            order.update(arg)
        order.update(kwargs)
        return self.__class__(self, _index=self.index.order_by(order))

    @property
    def availability(self):
        # TODO: move this to the right location

        if self._availability is not None:
            return self._availability.tree()

        def f():
            for i in self.index.db.dump_dicts():
                i = {k: v for k, v in i.items() if not k.startswith("_")}
                yield i

        LOG.debug("Building availability")
        from climetlab.utils.availability import Availability

        self._availability = Availability(f())
        return self.availability


source = DirectorySource
