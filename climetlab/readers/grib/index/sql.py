# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
from collections import namedtuple

from climetlab.decorators import cached_method
from climetlab.indexing.database.sql import SqlDatabase, SqlOrder, SqlSelection
from climetlab.readers.grib.index.db import FieldsetInFilesWithDBIndex
from climetlab.utils.serialise import register_serialisation

LOG = logging.getLogger(__name__)

SqlResultCache = namedtuple("SqlResultCache", ["first", "length", "result"])


class FieldsetInFilesWithSqlIndex(FieldsetInFilesWithDBIndex):
    DBCLASS = SqlDatabase
    DB_CACHE_SIZE = 100_000
    DB_DICT_CACHE_SIZE = 100_000

    def __init__(self, *args, **kwargs):
        """
        _filters are used to keep the state of the db
        It is a list of **already applied** filters, not a list of filter to apply.
        Use the method apply_filters for this.
        """

        super().__init__(*args, **kwargs)

    def apply_filters(self, filters):
        obj = self
        for f in filters:
            obj = obj.filter(f)
        return obj

    def _find_all_coords_dict(self):
        return self.db._find_all_coords_dict()

    def filter(self, filter):
        db = self.db.filter(filter)
        return self.__class__(db=db)

    def sel(self, *args, **kwargs):
        kwargs = self.normalize_selection(*args, **kwargs)
        if not kwargs:
            return self
        return self.filter(SqlSelection(kwargs))

    def order_by(self, *args, **kwargs):
        kwargs = self.normalize_order_by(*args, **kwargs)
        if not kwargs:
            return self
        return self.filter(SqlOrder(kwargs))

    def part(self, n):
        if self._cache is None or not (
            self._cache.first <= n < self._cache.first + self._cache.length
        ):
            first = (n // self.DB_CACHE_SIZE) * self.DB_CACHE_SIZE
            result = self.db.lookup_parts(limit=self.DB_CACHE_SIZE, offset=first)
            self._cache = SqlResultCache(first, len(result), result)
        return self._cache.result[n % self.DB_CACHE_SIZE]

    def get_metadata(self, n):
        if self._dict_cache is None or not (
            self._dict_cache.first
            <= n
            < self._dict_cache.first + self._dict_cache.length
        ):
            first = (n // self.DB_DICT_CACHE_SIZE) * self.DB_DICT_CACHE_SIZE
            result = self.db.lookup_dicts(
                limit=self.DB_DICT_CACHE_SIZE,
                offset=first,
                with_parts=False,
                # remove_none=False ?
            )
            result = list(result)

            self._dict_cache = SqlResultCache(first, len(result), result)
        return self._dict_cache.result[n % self.DB_DICT_CACHE_SIZE]

    @cached_method
    def number_of_parts(self):
        return self.db.count()


register_serialisation(
    FieldsetInFilesWithSqlIndex,
    lambda x: [x.db.db_path, x.db._filters],
    lambda x: FieldsetInFilesWithSqlIndex(db=SqlDatabase(x[0])).apply_filters(
        filters=x[1]
    ),
)
