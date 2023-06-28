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

from climetlab.exceptions import NotIndexedDirectoryError
from climetlab.readers.grib.index.sql import FieldsetInFilesWithSqlIndex
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


class GenericDirectorySource(IndexedSource):
    """Abstract class, INDEX_CLASS must be implemented"""

    INDEX_CLASS = None

    DEFAULT_JSON_FILE = "climetlab.index"
    DEFAULT_DB_FILE = "climetlab-2.db"

    def __init__(
        self,
        path,
        db_path=None,
        _index=None,
        **kwargs,
    ):
        """
        index_file: optional
            The input index location. Must be a JSON file.
            If None, parse the actual files in the directory pointed by "path".
        db_path: optional
            The actual used database file. Must be a SQL CliMetLab index file.
            If None, create one in the default location.

        If _index is not None, ignore all other arguments (for internal usage)
        """

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
        if not os.path.exists(db_path):
            raise NotIndexedDirectoryError(
                f"This directory has not been indexed. Try running 'climetlab index_directory {self.path}'."
            )

        LOG.info(f"Using index file {db_path}")
        index = self.INDEX_CLASS.from_existing_db(db_path=db_path)
        super().__init__(index, **kwargs)


class IndexedDirectorySource(GenericDirectorySource):
    INDEX_CLASS = FieldsetInFilesWithSqlIndex


source = IndexedDirectorySource
