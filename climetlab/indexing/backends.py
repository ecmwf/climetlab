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
import pickle
import sqlite3
from datetime import datetime

import requests
from multiurl import robust

import climetlab as cml
from climetlab.core.caching import cache_file
from climetlab.profiling import timer
from climetlab.utils import download_and_cache, tqdm


class SqlJsonHelper:
    def __init__(self, filename):
        self.filename = filename
        self.connection = None

    def create_connection(self, target, names):
        if os.path.exists(target):
            os.unlink(target)
        self.connection = sqlite3.connect(target)

        assert "offset" not in names
        assert "length" not in names
        self.sql_names = [f"i_{n}" for n in names]
        others = ",".join([f"{n} TEXT" for n in self.sql_names])

        create_statement = f"""CREATE TABLE entries (
            offset  INTEGER,
            length  INTEGER,
            {others} 
            );"""
        self.connection.execute(create_statement)

        commas = ",".join(["?" for _ in names])
        self.insert_statement = f"""INSERT INTO entries(
                                           offset, length, {','.join(self.sql_names)}) 
                                           VALUES(?,?,{commas});"""

    def to_sql_target(self, target):
        count = 0
        size = None
        names = None
        if os.path.exists(self.filename):
            iterator = open(self.filename).readlines()
            size = os.path.getsize(self.filename)
        else:
            r = robust(requests.get)(self.filename, stream=True)
            r.raise_for_status()
            try:
                size = int(r.headers.get("Content-Length"))
            except Exception:
                pass
            iterator = r.iter_lines()

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
            if self.connection is None:
                names = [n for n in sorted(entry.keys()) if not n.startswith("_")]
                self.create_connection(target, names)
            assert names is not None, names
            _names = [n for n in sorted(entry.keys()) if not n.startswith("_")]
            assert _names == names, (names, _names)
            values = [entry["_offset"], entry["_length"]] + [entry[n] for n in names]
            self.connection.execute(self.insert_statement, tuple(values))
            count += 1
            pbar.update(len(line) + 1)

        # for n in self.sql_names:
        #     self.connection.execute(f"""CREATE INDEX {n}_index ON entries ({n});""")
        self.connection.execute("COMMIT;")


def json_to_sql(target, filename):
    helper = SqlJsonHelper(filename)
    helper.to_sql_target(target)


class IndexBackend:
    pass


class JsonIndexBackend(IndexBackend):
    def __init__(self, url):
        # if os.path.exists(url):
        #    path = url
        # else:
        #    path = download_and_cache(url)
        path = cache_file("index", json_to_sql, url, extension=".db")
        self.connection = sqlite3.connect(path)

    def lookup(self, request):
        parts = []
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
        statement = f"SELECT offset,length FROM entries WHERE {' AND '.join(conditions)} ORDER BY offset;"
        for offset, length in self.connection.execute(statement):
            parts.append((None, (offset, length)))
        return parts
