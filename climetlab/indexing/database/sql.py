# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import hashlib
import json
import logging
import os
import sqlite3

import climetlab as cml
from climetlab.core.index import Order, Selection
from climetlab.utils import tqdm
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
    # "latitude",  # in the MARS vocabulary but not used.
    # "longitude",  # in the MARS vocabulary but not used.
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

    def __init__(self, db_path, view_name="entries", _connection=None):

        self.view_name = view_name
        self.db_path = db_path
        self._connection = _connection

        LOG.debug("DB %s %s", self.db_path, self.view_name)

    @property
    def connection(self):
        if self._connection is None:
            print(f"Connecting to DB ({self.db_path})")
            self._connection = sqlite3.connect(self.db_path)
        return self._connection

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

            # connection.execute(f"CREATE INDEX path_index ON entries (path);")
            pbar = tqdm(i_columns + ["path"], desc="Building indexes")
            for n in pbar:
                pbar.set_description(f"Building index for {n}")
                conn.execute(f"CREATE INDEX IF NOT EXISTS {n}_index ON entries ({n});")

            return count

    def _conditions(self, selection):
        conditions = []
        for k, b in selection.dic.items():
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

    def _order_by(self, order, view_name):
        """Uses a Order object to help building an SQL query.

        Input: a Order object
        Return: (dict, func_name, func)
        The dict should be merged to create an "ORDER BY" SQL string
        The function can be use to feed the SQL connection.create_function()
        """

        if not order:
            return None, None
        assert isinstance(order, Order), order

        # TODO: add default ordering
        # TODO: To improve speed, we could use ASC or DESC when lst is already sorted
        # TODO: move GRIB_INDEX_KEYS and two comments above to upper class

        dict_of_dicts = dict()
        order_lst = []

        # Use mars keys order by default
        # But make sure the order provided by the user
        # in the order override this default order.
        keys = [_ for _ in order.order.keys()]
        keys += [_ for _ in GRIB_INDEX_KEYS if _ not in keys]

        order_func_name = None
        for key in keys:
            lst = order.order.get(key, "ascending")  # Default is ascending order

            if lst is None:
                order_lst.append(f"i_{key}")
                continue

            if lst == "ascending":
                order_lst.append(f"i_{key} ASC")
                continue

            if lst == "descending":
                order_lst.append(f"i_{key} DESC")
                continue

            if not isinstance(lst, (list, tuple)):
                lst = [lst]

            lst = [str(_) for _ in lst]  # processing only strings from now.

            dict_of_dicts[key] = dict(zip(lst, range(len(lst))))
            order_func_name = f"userorder_{view_name}"
            order_lst.append(f'{order_func_name}("{key}",i_{key})')

        def order_func(key, value):
            return dict_of_dicts[key][value]

        return order_lst, order_func_name, order_func

    def _columns_names_without_i_(self):
        cursor = self.connection.execute("PRAGMA table_info(entries)")
        out = []
        for x in cursor.fetchall():
            name = x[1]
            if name.startswith("i_"):
                name = name[2:]  # remove "i_"
                out.append(name)
        return out

    def sel(self, selection: Selection):
        view_name = self.view_name + "_" + selection.h()
        print(f"Creating sel view {view_name}.")
        connection = self.connection

        conditions = self._conditions(selection)
        conditions_str = " WHERE " + " AND ".join(conditions) if conditions else ""
        statement = f"CREATE TEMP VIEW IF NOT EXISTS {view_name} AS SELECT * FROM {self.view_name} {conditions_str};"

        LOG.debug("%s", statement)
        print(statement)
        for i in connection.execute(statement):
            LOG.error(str(i))

        return self.__class__(
            self.db_path, view_name=view_name, _connection=self._connection
        )

    def order_by(self, order: Order):
        view_name = self.view_name + "_" + order.h()
        print(f"Creating order view {view_name}.")
        connection = self.connection

        order_by, order_func_name, order_func = self._order_by(order, view_name)
        order_by_str = "ORDER BY " + ",".join(order_by) if order_by else ""
        if order_func_name is not None:
            print(f'create_function: {order_func_name}"')
            connection.create_function(order_func_name, 2, order_func)
        statement = (
            f"CREATE TEMP VIEW IF NOT EXISTS {view_name} AS SELECT * FROM {self.view_name} {order_by_str};"
        )

        LOG.debug("%s", statement)
        print(statement)
        for i in connection.execute(statement):
            LOG.error(str(i))

        return self.__class__(
            self.db_path, view_name=view_name, _connection=self._connection
        )

    def lookup_parts(self, limit=None, offset=None, resolve_paths=True):
        """
        Look into the database and provide entries as Parts.
        limit: Returns only "limit" entries (used for paging).
        offset: Skip the first "offset" entries (used for paging).
        """

        _names = ["path", "offset", "length"]
        parts = []
        for path, offset, length in self._execute_select(_names, limit, offset):
            parts.append(Part(path, offset, length))
        if resolve_paths:
            parts = Part.resolve(parts, os.path.dirname(self.db_path))
        return parts

    def lookup_dicts(self, keys=None, limit=None, offset=None):
        """
        From a list of keys, return dicts with these columns of the database.
        limit: Returns only "limit" entries (used for paging).
        offset: Skip the first "offset" entries (used for paging).
        """
        if keys is None:
            keys = self._columns_names_without_i_()
        assert isinstance(keys, (list, tuple)), keys

        _names = [f"i_{x}" for x in keys]
        dicts = []
        for tupl in self._execute_select(_names, limit, offset):
            dic = {k: v for k, v in zip(_names, tupl)}
            dicts.append(dic)
        return dicts

    def _execute_select(self, names, limit, offset):
        names_str = ",".join([x for x in names]) if names else "*"
        limit_str = f" LIMIT {limit}" if limit is not None else ""
        offset_str = f" OFFSET {offset}" if offset is not None else ""

        statement = (
            f"SELECT {names_str} FROM {self.view_name} {limit_str} {offset_str};"
        )
        LOG.debug("%s", statement)

        for tupl in self.connection.execute(statement):
            yield tupl

    def count(self):
        statement = f"SELECT COUNT(*) FROM {self.view_name};"
        for result in self.connection.execute(statement):
            return result[0]
        assert False

    def _dump_dicts(self):
        names = self._columns_names_without_i_()
        names_str = ",".join([f"i_{x}" for x in names])
        statement = f"SELECT path,offset,length,{names_str} FROM entries ;"
        for tupl in self.connection.execute(statement):
            yield {k: v for k, v in zip(["_path", "_offset", "_length"] + names, tupl)}

    def dump_dicts(self, remove_none=True):
        for dic in self._dump_dicts():
            if remove_none:
                dic = {k: v for k, v in dic.items() if v is not None}
            yield dic

    def duplicate_db(self, filename, **kwargs):
        new = SqlDatabase(db_path=filename)
        new.load(self.dump_dicts(**kwargs))
