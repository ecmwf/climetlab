# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import json
import logging
import os
import sqlite3

import climetlab as cml
from climetlab.utils.parts import Part

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


def create_table(target, names):
    LOG.debug(f"Create_table connecting to {target}")
    if os.path.exists(target):
        os.unlink(target)
    connection = sqlite3.connect(target)

    all_names = [n for n in GRIB_INDEX_KEYS]
    for n in names:
        if n not in GRIB_INDEX_KEYS:
            all_names.append(n)
            LOG.debug(f"Warning: Adding an unknown grib index key {n}")
    sql_names = [f"i_{n}" for n in all_names]

    sql_names_headers = ",".join([f"{n} TEXT" for n in sql_names])
    create_statement = f"""CREATE TABLE entries (
        path    TEXT,
        offset  INTEGER,
        length  INTEGER,
        {sql_names_headers}
        );"""
    LOG.debug(create_statement)
    connection.execute(create_statement)

    commas = ",".join(["?" for _ in sql_names])
    insert_statement = f"""INSERT INTO entries(
                                       path, offset, length, {','.join(sql_names)})
                                       VALUES(?,?,?,{commas});"""
    return connection, insert_statement, sql_names, all_names


class Database:
    def lookup(self, request, order=None):
        raise NotImplementedError("")

    def reset_connection(self, *args, **kwargs):
        raise NotImplementedError("")


class JsonDatabase(Database):
    def __init__(
        self,
        db_path,
        iterator=None,
    ):
        self.entries = list(iterator)

        if not os.path.exists(db_path):
            # TODO: any bug here?
            # due to unfinished download in cache?
            # or concurrent download?
            with open(db_path, "w") as f:
                for entry in self.entries:
                    f.write(json.dumps(entry) + "\n")

    def lookup(self, request, **kwargs):

        if kwargs.get("order") is not None:
            raise NotImplementedError()

        if request is None:
            return self.entries

        parts = []
        for e in self.entries:
            for k, v in e.items():
                if v not in request.get(k, []):
                    continue
            parts.append(Part(e["_path"], e["_offset"], e["_length"]))
        return parts

    def reset_connection(self, *args, **kwargs):
        pass


class SqlDatabase(Database):
    VERSION = 2

    def __init__(
        self,
        db_path,
        iterator=None,
        create_index_in_sql_db=False,  # index is disabled by default because it is long to create.
        # create_entry_in_db=None,
    ):
        self._connection = None
        self.db_path = db_path

        self.create_index_in_sql_db = create_index_in_sql_db

        if iterator is not None:
            self.load(iterator)

    def reset_connection(self, db_path):
        self._connection = None
        self.db_path = db_path

    @property
    def connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
        LOG.debug(f"Connecting to db in {self.db_path}")
        return self._connection

    def load(self, iterator):
        # is_url = (
        #    url.startswith("http://")
        #    or url.startswith("https://")
        #    or url.startswith("ftp://")
        # )

        count = 0
        names = None
        connection = None
        insert_statement = None

        for entry in iterator:
            if connection is None:
                # this is done only for the first entry only
                names = [n for n in sorted(entry.keys()) if not n.startswith("_")]
                connection, insert_statement, sql_names, all_names = create_table(
                    self.db_path, names
                )

            assert names is not None, names
            assert connection is not None, connection
            assert insert_statement is not None
            assert len(sql_names) == len(all_names), (sql_names, all_names)

            # additional check is disabled
            # _names = [n for n in sorted(entry.keys()) if not n.startswith("_")]
            # assert _names == names, (names, _names)
            path, offset, length = entry["_path"], entry["_offset"], entry["_length"]
            # if path is not None:
            #    if is_url:
            #        from urllib.parse import urljoin
            #        path = urljoin(url, path)
            #
            #    else:
            #        if not os.path.isabs(path):
            #            path = os.path.join(os.path.dirname(url), path)
            # else:
            #    path = self.the_path_from__init__

            values = [path, offset, length] + [entry.get(n, None) for n in all_names]

            LOG.debug(insert_statement)
            connection.execute(insert_statement, tuple(values))

            count += 1

        if self.create_index_in_sql_db:
            # connection.execute(f"CREATE INDEX path_index ON entries (path);")
            for n in sql_names:
                connection.execute(f"CREATE INDEX {n}_index ON entries ({n});")

        connection.execute("COMMIT;")
        connection.close()

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

    def lookup(self, request, select_values=False, order=None, limit=None, offset=None):
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

        if select_values:
            if select_values is True:
                select_values = self._columns_names_without_i_()

            select_values_str = ",".join([f"i_{x}" for x in select_values])
            statement = f"SELECT {select_values_str} FROM entries {conditions_str} {order_by_str};"

            LOG.debug(statement)
            parts = []
            for tupl in self.connection.execute(statement):
                dic = {k: v for k, v in zip(select_values, tupl)}
                parts.append(dic)
            return parts

        else:
            statement = f"SELECT path,offset,length FROM entries {conditions_str} {order_by_str};"

            LOG.debug(statement)
            parts = []
            for path, offset, length in self.connection.execute(statement):
                parts.append(Part(path, offset, length))
            return parts
