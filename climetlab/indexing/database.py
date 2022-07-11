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

import requests
from multiurl import robust

import climetlab as cml
from climetlab.core.caching import cache_file
from climetlab.utils import tqdm

LOG = logging.getLogger(__name__)


def get_iterator_and_size_from_path(path):
    iterator = open(path).readlines()
    size = os.path.getsize(path)
    return iterator, size


def get_iterator_and_size(url):
    if os.path.exists(url):
        return get_iterator_and_size_from_path(path=url)

    if url.startswith("file://") and os.path.exists(url[7:]):
        return get_iterator_and_size_from_path(path=url[7:])

    r = robust(requests.get)(url, stream=True)
    r.raise_for_status()
    try:
        size = int(r.headers.get("Content-Length"))
    except Exception:
        size = None
    iterator = r.iter_lines()
    return iterator, size


GRIB_INDEX_KEYS = [
    "class",
    "stream",
    "levtype",
    "type",
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
    "expver",
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


class SqlDatabase(Database):
    VERSION = 2

    def __init__(
        self,
        url,
        create_index_in_sql_db=False,  # index is disabled by default because it is long to create.
    ):
        self._connection = None
        self.url = url
        self.create_index_in_sql_db = create_index_in_sql_db

    @property
    def connection(self):
        if self._connection is None:
            path = cache_file(
                "index",
                self.to_sql_target,
                self.url,
                hash_extra=self.VERSION,
                extension=".db",
            )
            self._connection = sqlite3.connect(path)
        return self._connection

    def to_sql_target(self, target, url):
        iterator, size = get_iterator_and_size(url)

        count = 0
        names = None
        connection = None
        insert_statement = None
        pbar = tqdm(
            iterator,
            desc="Downloading index",
            total=size,
            unit_scale=True,
            unit="B",
            leave=False,
            disable=False,
            unit_divisor=1024,
        )
        for line in pbar:
            entry = json.loads(line)
            if connection is None:
                # this is done only for the first entry only
                names = [n for n in sorted(entry.keys()) if not n.startswith("_")]
                connection, insert_statement, sql_names, all_names = create_table(
                    target, names
                )

            assert names is not None, names
            assert connection is not None, connection
            assert insert_statement is not None
            assert len(sql_names) == len(all_names), (sql_names, all_names)

            # additional check is disabled
            # _names = [n for n in sorted(entry.keys()) if not n.startswith("_")]
            # assert _names == names, (names, _names)

            values = [entry.get("_path", None), entry["_offset"], entry["_length"]] + [
                entry.get(n, None) for n in all_names
            ]
            LOG.debug(insert_statement)

            connection.execute(insert_statement, tuple(values))

            count += 1
            pbar.update(len(line) + 1)

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

        if order == True:
            if not request:
                return None
            return [f"i_{k}" for k in request.keys()]

        if isinstance(order, str):
            return [order]

        raise NotImplementedError(str(order))

    def _columns_names_with_no_i_(self):
        cursor = self.connection.execute("PRAGMA table_info(entries)")
        out = []
        for x in cursor.fetchall():
            name = x[1]
            if name.startswith("i_"):
                name = name[2:]  # remove "i_"
                out.append(name)
        return out

    def lookup(self, request, select_values=False, order=None):

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
                select_values = self._columns_names_with_no_i_()

            select_values_str = ",".join([f"i_{x}" for x in select_values])
            statement = f"SELECT {select_values_str} FROM entries {conditions_str} {order_by_str};"

            LOG.debug(statement)
            parts = []
            for tupl in self.connection.execute(statement):
                dic = {k: v for k, v in zip(select_values, tupl)}
                parts.append(dic)

        else:
            statement = (
                f"SELECT path,offset,length FROM entries {conditions_str} {order_by};"
            )

            LOG.debug(statement)
            parts = []
            for path, offset, length in self.connection.execute(statement):
                parts.append((path, (offset, length)))

        return parts
