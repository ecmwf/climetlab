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

from climetlab.scripts.grib import _index_grib_file
from climetlab.sources.indexed import IndexedSource, JsonIndex, SqlIndex

LOG = logging.getLogger(__name__)


class DirectorySource(IndexedSource):
    INDEX_BASE_FILENAME = "climetlab.index"

    def __init__(self, path, index_next_to_data=True, index_type="sql", **kwargs):
        self.path = path
        self.abspath = os.path.abspath(path)

        IndexClass = {
            "sql": SqlIndex,
            "json": JsonIndex,
        }[index_type]
        extension = {"sql": ".db", "json": ".json"}[index_type]

        self._db_path = None
        if index_next_to_data:
            self._db_path = os.path.join(
                self.abspath,
                self.INDEX_BASE_FILENAME + extension,
            )

        entries = self._parse_files(path)

        index = IndexClass.from_scanner(
            entries,
            db_path=self._db_path,
            cache_metadata={"directory": self.path},
        )

        super().__init__(index, **kwargs)

    def _parse_files(self, path):
        ignore = ["climetlab.index", "climetlab.index.db"]
        ignore.append(self._db_path)

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
