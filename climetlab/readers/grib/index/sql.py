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

from climetlab.core.constants import DATETIME
from climetlab.core.order import normalize_order_by
from climetlab.core.select import normalize_selection
from climetlab.decorators import cached_method, normalize, normalize_grib_key_values
from climetlab.indexing.database.sql import (
    SqlDatabase,
    SqlOrder,
    SqlRemapping,
    SqlSelection,
)
from climetlab.loaders import build_remapping
from climetlab.readers.grib.index.db import FieldsetInFilesWithDBIndex
from climetlab.utils.serialise import register_serialisation

LOG = logging.getLogger(__name__)

SqlResultCache = namedtuple("SqlResultCache", ["first", "length", "result"])


@normalize(DATETIME, "date-list", format="%Y-%m-%d %H:%M:%S")
def _normalize_grib_kwargs_values(**kwargs):
    return kwargs


class FieldsetInFilesWithSqlIndex(FieldsetInFilesWithDBIndex):
    DBCLASS = SqlDatabase
    DB_CACHE_SIZE = 100_000
    DB_DICT_CACHE_SIZE = 100_000

    def apply_filters(self, filters):
        obj = self
        for f in filters:
            obj = obj.filter(f)
        return obj

    def _find_all_coords_dict(self):
        return self.db._find_all_coords_dict()

    def unique_values(self, *coords, remapping=None, progress_bar=None):
        """
        Given a list of metadata attributes, such as date, param, levels,
        returns the list of unique values for each attributes
        """
        keys = coords

        remapping = build_remapping(remapping)
        print("Not using remapping here")

        coords = {k: None for k in coords}
        coords = self._normalize_kwargs_names(**coords)
        coords = list(coords.keys())
        print("coords:", coords)
        values = self.db.unique_values(*coords, remapping=remapping).values()

        dic = {k: v for k, v in zip(keys, values)}
        return dic

    def filter(self, filter):
        db = self.db.filter(filter)
        return self.__class__(db=db)

    def sel(self, *args, remapping=None, **kwargs):
        kwargs = normalize_selection(*args, **kwargs)
        kwargs = self._normalize_kwargs_names(**kwargs)
        kwargs = normalize_grib_key_values(kwargs, as_tuple=True)
        if DATETIME in kwargs and kwargs[DATETIME] is not None:
            kwargs = _normalize_grib_kwargs_values(**kwargs)

        if not kwargs:
            return self
        return self.filter(SqlSelection(kwargs, remapping))

    def order_by(self, *args, remapping=None, **kwargs):
        kwargs = normalize_order_by(*args, **kwargs)
        kwargs = self._normalize_kwargs_names(**kwargs)

        out = self

        if remapping is not None:
            out = out.filter(SqlRemapping(remapping=remapping))

        if kwargs:
            out = out.filter(SqlOrder(kwargs))

        return out

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
