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

    def __init__(
        self,
        db_path,
        create_index=True,
    ):

        self.db_path = db_path
        self.create_index = create_index

        LOG.debug("DB %s", self.db_path)

    @property
    def connection(self):
        return sqlite3.connect(self.db_path)

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
                pbar = tqdm(i_columns + ["path"], desc="Building indexes")
                for n in pbar:
                    pbar.set_description(f"Building index for {n}")
                    conn.execute(
                        f"CREATE INDEX IF NOT EXISTS {n}_index ON entries ({n});"
                    )

            return count

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

    def _order_by(self, order):
        if not order:
            return None, None
        print("ORDER=", order)
        if order is True:
            if not order:
                return None
            return [f"i_{k}" for k in order.keys()], None

        # TODO: add default ordering
        dict_of_dicts = dict()
        order_lst = []

        # Use mars keys order by default
        # But make sure the order provided by the user
        # in the order override this default order.
        keys = [_ for _ in order.keys()]
        keys += [_ for _ in GRIB_INDEX_KEYS if _ not in keys]

        for key in keys:
            lst = order.get(key, "ascending")  # Default is ascending order

            if lst is None:
                order_lst.append(f"i_{key}")
                continue

            if lst == "ascending":
                order_lst.append(f"i_{key} ASC")
                continue

            if lst == "descending":
                order_lst.append(f"i_{key} DESC")
                continue

            # TODO: To improve speed, we could use ASC or DESC when lst is already sorted

            if not isinstance(lst, (list, tuple)):
                lst = [lst]

            lst = [str(_) for _ in lst]  # processing only strings from now.

            dict_of_dicts[key] = dict(zip(lst, range(len(lst))))
            print(key, lst)
            order_lst.append(f'user_order("{key}",i_{key})')

        def order_func(key, value):
            return dict_of_dicts[key][value]

        return order_lst, order_func

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
        return_dicts=False,
        order=None,
        limit=None,
        offset=None,
    ):
        """Look into the database and provide entries.

        request: a dictionary containing the list of values to filter by.
        return_dicts: Return dictionaries of entries instead of (path resolved) Part objects.
        order: a dictionary to order the entries.
        limit: Returns only "limit" entries (used for paging).
        offset: Skip the first "offset" entries (used for paging).
        """
        if request is None:
            request = {}
        if order is None:
            order = request

        conditions_str = ""
        conditions = self._conditions(request)
        if conditions:
            conditions_str = " WHERE " + " AND ".join(conditions)

        paging_str = ""
        if limit is not None:
            paging_str += f" LIMIT {limit}"

        if offset is not None:
            paging_str += f" OFFSET {offset}"

        order_by_str = ""
        order_by, order_func = self._order_by(order)
        if order_by:
            order_by_str = "ORDER BY " + ",".join(order_by)

        connection = self.connection
        if order_func is not None:
            connection.create_function("user_order", 2, order_func)

        if return_dicts:
            _names = self._columns_names_without_i_()
            _names_str = ",".join([f"i_{x}" for x in _names])
            statement = f"SELECT {_names_str} FROM entries {conditions_str} {order_by_str} {paging_str};"

            LOG.debug("%s", statement)
            parts = []
            for tupl in connection.execute(statement):
                dic = {k: v for k, v in zip(_names, tupl)}
                parts.append(dic)
            return parts

        statement = f"SELECT path,offset,length FROM entries {conditions_str} {order_by_str} {paging_str};"
        print(statement)
        LOG.debug("%s", statement)
        parts = []
        for path, offset, length in connection.execute(statement):
            parts.append(Part(path, offset, length))
        return Part.resolve(parts, os.path.dirname(self.db_path))

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
