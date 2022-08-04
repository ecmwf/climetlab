# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging
import os
import sqlite3

import climetlab as cml
from climetlab.utils.parts import Part

from . import Database

LOG = logging.getLogger(__name__)


GRIB_INDEX_KEYS = [
    "class",
    "stream",
    "levtype",
    "type",
    "expver",
    "date",
    "hdate",
    "andate",
    "time",
    "antime",
    "reference",
    "step",
    "anoffset",
    "verify",
    "fcmonth",
    "fcperiod",
    "leadtime",
    "opttime",
    "origin",
    "domain",
    "method",
    "diagnostic",
    "iteration",
    "number",
    "quantile",
    "levelist",
    "latitude",
    "longitude",
    "range",
    "param",
    "ident",
    "obstype",
    "instrument",
    "reportype",
    "frequency",  # for 2-d wave-spectra products
    "direction",  # for 2-d wave-spectra products
    "channel",  # for ea, ef
]


class SqlDatabase(Database):
    VERSION = 3
    EXTENSION = ".db"

    def __init__(
        self,
        db_path,
        create_index=False,  # index is disabled by default because it is long to create.
    ):

        self.db_path = db_path
        self.create_index = create_index
        self.connection = sqlite3.connect(self.db_path)

        LOG.debug("DB %s", self.db_path)

    def load(self, iterator):
        with self.connection as conn:

            # The i_ is to avoid clashes with SQL keywords
            i_columns = [f"i_{n}" for n in GRIB_INDEX_KEYS]
            columns_defs = ",".join([f"{c} TEXT" for c in i_columns])
            create_statement = f"""CREATE TABLE IF NOT EXISTS entries (
                path    TEXT,
                offset  INTEGER,
                length  INTEGER,
                {columns_defs}
                );"""
            LOG.debug("%s", create_statement)
            conn.execute(create_statement)

            columns = ",".join(i_columns)
            values = ",".join(["?"] * (3 + len(i_columns)))
            insert_statement = f"""
            INSERT INTO entries (path, offset, length, {columns})
            VALUES({values});
            """
            LOG.debug("%s", insert_statement)

            count = 0

            for entry in iterator:
                assert isinstance(entry, dict), (type(entry), entry)
                values = [entry["_path"], entry["_offset"], entry["_length"]] + [
                    entry.get(n) for n in GRIB_INDEX_KEYS
                ]
                conn.execute(insert_statement, tuple(values))
                count += 1

            assert count >= 1
            LOG.info("Added %d entries", count)

            if self.create_index:
                # connection.execute(f"CREATE INDEX path_index ON entries (path);")
                for n in i_columns:
                    conn.execute(
                        f"CREATE INDEX IF NOT EXISTS {n}_index ON entries ({n});"
                    )

    def _conditions(self, request):
        conditions = []
        for k, b in request.items():
            if b is None or b == cml.ALL:
                continue
            elif isinstance(b, (list, tuple)):
                if len(b) == 1:
                    conditions.append(f"i_{k}='{b[0]}'")
                    continue
                w = ",".join([f"'{x}'" for x in b])
                conditions.append(f"i_{k} IN ({w})")
            else:
                conditions.append(f"i_{k}='{b}'")
        return conditions

    def _order_by(self, request, order):
        if order is None:
            return None

        if order is True:
            if not request:
                return None
            return [f"i_{k}" for k in request.keys()]

        if isinstance(order, str):
            return [order]

        if isinstance(order, (list, tuple)):
            return order

        raise NotImplementedError(str(order))

    def _columns_names_without_i_(self):
        cursor = self.connection.execute("PRAGMA table_info(entries)")
        out = []
        for x in cursor.fetchall():
            name = x[1]
            if name.startswith("i_"):
                name = name[2:]  # remove "i_"
                out.append(name)
        return out

    def count(self, request):
        if request is None:
            request = {}

        conditions_str = ""
        conditions = self._conditions(request)
        if conditions:
            conditions_str = " WHERE " + " AND ".join(conditions)

        statement = f"SELECT COUNT(*) FROM entries {conditions_str};"

        LOG.debug(statement)
        for result in self.connection.execute(statement):
            return result[0]
        assert False

    def lookup(
        self,
        request,
        select_values=False,
        order=None,
        limit=None,
        offset=None,
    ):
        if request is None:
            request = {}

        conditions_str = ""
        conditions = self._conditions(request)
        if conditions:
            conditions_str = " WHERE " + " AND ".join(conditions)

        order_by_str = ""
        order_by = self._order_by(request, order)
        if order_by:
            order_by_str = "ORDER BY " + ",".join(order_by)

        paging_str = ""
        if limit is not None:
            paging_str += f" LIMIT {limit}"

        if offset is not None:
            paging_str += f" OFFSET {offset}"

        if select_values:
            if select_values is True:
                select_values = self._columns_names_without_i_()

            select_values_str = ",".join([f"i_{x}" for x in select_values])
            statement = f"SELECT {select_values_str} FROM entries {conditions_str} {order_by_str} {paging_str};"

            LOG.debug("%s", statement)
            parts = []
            for tupl in self.connection.execute(statement):
                dic = {k: v for k, v in zip(select_values, tupl)}
                parts.append(dic)
            return parts

        statement = f"SELECT path,offset,length FROM entries {conditions_str} {order_by_str} {paging_str};"
        LOG.debug("%s", statement)
        parts = []
        for path, offset, length in self.connection.execute(statement):
            parts.append(Part(path, offset, length))
        return Part.resolve(parts, os.path.dirname(self.db_path))

    def _dump_dicts(self):
        names = self._columns_names_without_i_()
        names_str = ",".join([f"i_{x}" for x in names])
        statement = f"SELECT path,offset,length,{names_str} FROM entries ;"
        for tupl in self.connection.execute(statement):
            yield {k: v for k, v in zip(["_path", "_offset", "_length"] + names, tupl)}

    def dump_dicts(self, remove_none=True):
        def do_remove_none(dic):
            return {k: v for k, v in dic.items() if v is not None}

        for dic in self._dump_dicts():
            if remove_none:
                dic = do_remove_none(dic)

            yield dic

    def duplicate_db(self, filename, **kwargs):
        new = SqlDatabase(db_path=filename)
        new.load(self.dump_dicts(**kwargs))
