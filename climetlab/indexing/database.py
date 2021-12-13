# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import json
import os
import sqlite3

import requests
from multiurl import robust

from climetlab.core.caching import cache_file
from climetlab.utils import tqdm


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


def create_table(target, names):
    if os.path.exists(target):
        os.unlink(target)
    connection = sqlite3.connect(target)

    sql_names = [f"i_{n}" for n in names]
    others = ",".join([f"{n} TEXT" for n in sql_names])

    create_statement = f"""CREATE TABLE entries (
        path    TEXT,
        offset  INTEGER,
        length  INTEGER,
        {others}
        );"""
    connection.execute(create_statement)

    commas = ",".join(["?" for _ in names])
    insert_statement = f"""INSERT INTO entries(
                                       path, offset, length, {','.join(sql_names)})
                                       VALUES(?,?,?,{commas});"""
    return connection, insert_statement, sql_names


class Database:
    def lookup(self, request):
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
                connection, insert_statement, sql_names = create_table(target, names)

            assert names is not None, names
            assert connection is not None, connection
            assert insert_statement is not None
            assert len(sql_names) == len(names), (sql_names, names)

            # additional check is disabled
            # _names = [n for n in sorted(entry.keys()) if not n.startswith("_")]
            # assert _names == names, (names, _names)

            values = [entry.get("_path", None), entry["_offset"], entry["_length"]] + [
                entry[n] for n in names
            ]
            connection.execute(insert_statement, tuple(values))

            count += 1
            pbar.update(len(line) + 1)

        if self.create_index:
            # connection.execute(f"CREATE INDEX path_index ON entries (path);")
            for n in sql_names:
                connection.execute(f"CREATE INDEX {n}_index ON entries ({n});")

        connection.execute("COMMIT;")
        connection.close()

    def lookup(self, request):
        conditions = []
        for k, b in request.items():
            if isinstance(b, (list, tuple)):
                if len(b) == 1:
                    conditions.append(f"i_{k}='{b[0]}'")
                    continue
                w = ",".join([f"'{x}'" for x in b])
                conditions.append(f"i_{k} IN ({w})")
            else:
                conditions.append(f"i_{k}='{b}'")

        statement = f"SELECT path,offset,length FROM entries WHERE {' AND '.join(conditions)} ORDER BY offset;"

        parts = []
        for path, offset, length in self.connection.execute(statement):
            parts.append((path, (offset, length)))
        return parts
