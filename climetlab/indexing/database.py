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

from climetlab.core.caching import cache_file
from climetlab.utils import tqdm

LOG = logging.getLogger(__name__)


def get_iterator_and_size(url):
    if os.path.exists(url):
        iterator = open(url).readlines()
        size = os.path.getsize(url)
        return iterator, size

    r = robust(requests.get)(url, stream=True)
    r.raise_for_status()
    try:
        size = int(r.headers.get("Content-Length"))
    except Exception:
        size = None
    iterator = r.iter_lines()
    return iterator, size


GRIB_INDEX_KEYS = [
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
        create_index=False,  # index is disabled by default because it is long to create.
    ):
        self._connection = None
        self.url = url
        self.create_index = create_index

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

        if self.create_index:
            # connection.execute(f"CREATE INDEX path_index ON entries (path);")
            for n in sql_names:
                connection.execute(f"CREATE INDEX {n}_index ON entries ({n});")

        connection.execute("COMMIT;")
        connection.close()

    def lookup(self, request, order=None):
        conditions = []
        for k, b in request.items():
            if b is None:
                continue
            elif isinstance(b, (list, tuple)):
                if len(b) == 1:
                    conditions.append(f"i_{k}='{b[0]}'")
                    continue
                w = ",".join([f"'{x}'" for x in b])
                conditions.append(f"i_{k} IN ({w})")
            else:
                conditions.append(f"i_{k}='{b}'")

        conditions_str = ""
        if conditions:
            conditions_str = " WHERE " + " AND ".join(conditions)

        def build_order_by(order):
            if order is None:
                return ""

            if order == True:
                if not request:
                    return ""
                order = [f"i_{k}" for k in request.keys()]
                return "ORDER BY " + ",".join(order)

            if isinstance(order, str):
                order = [order]

            if isinstance(order, (list, tuple)):
                return "ORDER BY " + ",".join(order)

            raise NotImplementedError(str(order))

        order_by = build_order_by(order)

        statement = (
            f"SELECT path,offset,length FROM entries {conditions_str} {order_by};"
        )

        LOG.debug(statement)
        parts = []
        for path, offset, length in self.connection.execute(statement):
            parts.append((path, (offset, length)))
        return parts
