# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import hashlib
import json
import logging
import os
import sqlite3
from abc import abstractmethod
from threading import local

import numpy as np

import climetlab as cml
from climetlab.utils import tqdm
from climetlab.utils.parts import Part

from . import (
    FILEPARTS_KEY_NAMES,
    MORE_KEY_NAMES,
    MORE_KEY_NAMES_WITH_UNDERSCORE,
    STATISTICS_KEY_NAMES,
    Database,
    FloatDBKey,
    IntDBKey,
    StrDBKey,
)

LOG = logging.getLogger(__name__)


def entryname_to_dbname(n):
    def add_mars(x):
        return "i_" + x

    def remove_first_underscore(x):
        assert x[0] == "_", x
        return x[1:]

    if n in FILEPARTS_KEY_NAMES:
        return remove_first_underscore(n)
    if n in MORE_KEY_NAMES_WITH_UNDERSCORE:
        return remove_first_underscore(n)
    if n in STATISTICS_KEY_NAMES:
        return n
    # if n in MORE_KEY_NAMES:
    #    return n
    return add_mars(n)


def dbname_to_entryname(n):
    if n.startswith("i_"):
        return n[2:]
    if "_" + n in FILEPARTS_KEY_NAMES:
        return "_" + n
    if "_" + n in MORE_KEY_NAMES_WITH_UNDERSCORE:
        return "_" + n
    if n in MORE_KEY_NAMES:
        return n
    return n


class EntriesLoader:
    table_name = "entries"

    def __init__(self, connection):
        self.connection = connection
        self.keys = self.read_from_table()

    @classmethod
    def guess_key_type(self, x, name=None):
        try:
            return {
                "TEXT": StrDBKey,
                "FLOAT": FloatDBKey,
                "INTEGER": IntDBKey,
                str: StrDBKey,
                float: FloatDBKey,
                np.float64: FloatDBKey,
                np.float32: FloatDBKey,
                int: IntDBKey,
                datetime.datetime: StrDBKey,
            }[x]
        except KeyError:
            raise ValueError(f"Unknown type '{x}' for key '{name}'.")

    def read_from_table(self):
        keys = {}
        cursor = self.connection.execute(f"PRAGMA table_info({self.table_name})")
        for x in cursor.fetchall():
            name, typ = x[1], x[2]
            klass = self.guess_key_type(typ, name)
            keys[name] = klass(name)

        if not keys:
            LOG.debug(f"Table {self.table_name} does not exist.")
        return keys

    def create_table_from_entry_if_needed(self, entry):
        keys = {}
        for k, v in entry.items():
            typ = type(v)
            klass = self.guess_key_type(typ, name=k)
            name = entryname_to_dbname(k)
            keys[name] = klass(name)

        assert keys, f"Cannot build from entry '{entry}'"
        LOG.debug(f"Created table {self} from entry {entry}.")
        columns_defs = ",".join([f"{v.name} {v.sql_type}" for k, v in keys.items()])
        statement = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({columns_defs});"
        LOG.debug("%s", statement)
        self.connection.execute(statement)
        return keys

    def load_iterator(self, iterator):
        count = 0
        for entry in iterator:
            if count == 0:
                self.keys = self.create_table_from_entry_if_needed(entry)
                column_names = [k for k, v in self.keys.items()]
                statement = (
                    f"INSERT INTO {self.table_name} ("
                    + ",".join(column_names)
                    + ") VALUES("
                    + ",".join(["?"] * len(column_names))
                    + ");"
                )
                LOG.debug("%s", statement)

            values = [entry.get(dbname_to_entryname(k)) for k, v in self.keys.items()]
            self.connection.execute(statement, tuple(values))
            count += 1

        self.build_sql_indexes()

        return count

    def build_sql_indexes(self):
        indexed_columns = [k for k, v in self.keys.items() if k.startswith("i_")]
        indexed_columns += ["path"]

        pbar = tqdm(indexed_columns, desc="Building indexes")
        for n in pbar:
            pbar.set_description(f"Building index for {n}")
            self.connection.execute(
                f"CREATE INDEX IF NOT EXISTS {n}_index ON {self.table_name} ({n});"
            )

    def __str__(self):
        content = ",".join([k for k, v in self.keys.items()])
        return f"{self.__class__}({self.table_name},{content}"


class Connection(local):
    # Inheriting from threading.local allows one connection for each thread
    # __init__ is "called each time the local object is used in a separate thread".
    # https://github.com/python/cpython/blob/0346eddbe933b5f1f56151bdebf5bd49392bc275/Lib/_threading_local.py#L65
    def __init__(self, db_path):
        self._conn = sqlite3.connect(db_path)


class SqlFilter:
    def h(self, *args, **kwargs):
        m = hashlib.sha256()
        m.update(str(args).encode("utf-8"))
        m.update(str(kwargs).encode("utf-8"))
        m.update(str(self.__class__.__name__).encode("utf-8"))
        m.update(json.dumps(self.kwargs, sort_keys=True).encode("utf-8"))
        return m.hexdigest()

    def __str__(self):
        return f"{self.__class__.__name__}({self.kwargs})"

    @property
    def is_empty(self):
        return not self.kwargs

    @abstractmethod
    def filter_statement(self, db, *args, **kwargs):
        pass


class SqlSelection(SqlFilter):
    def __init__(self, kwargs: dict):
        self.kwargs = kwargs

    def filter_statement(self, db, *args, **kwargs):
        conditions = []
        for k, v in self.kwargs.items():
            if v is None or v == cml.ALL:
                continue

            name = entryname_to_dbname(k)
            dbkey = db.dbkeys[name]

            if not isinstance(v, (list, tuple)):
                v = [v]

            v = [dbkey.cast(x) for x in v]
            v = ["'" + str(x) + "'" for x in v]

            conditions.append(f"{name} IN ({', '.join(v)})")

        if not conditions:
            return ""
        return " WHERE " + " AND ".join(conditions)


class SqlOrder(SqlFilter):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def filter_statement(self, db, new_view):
        func_name = "userorder_" + new_view

        order_bys = []
        dict_of_dicts = {}

        for k, v in self.kwargs.items():
            name = entryname_to_dbname(k)

            dbkey = db.dbkeys[name]

            if v == "ascending" or v is None:
                order_bys.append(name + " ASC")
                continue
            if v == "descending" or v is None:
                order_bys.append(name + " DESC")
                continue
            if isinstance(v, (list, tuple)):
                v = [dbkey.cast(x) for x in v]
                dict_of_dicts[name] = dict(zip(v, range(len(v))))
                order_bys.append(func_name + "(" + "'" + name + "'" + ", " + name + ")")
                continue

            raise ValueError(f"{k},{v}, {type(v)}")

        if dict_of_dicts:

            def order_func(k, v):
                return dict_of_dicts[k][v]

            db.connection.create_function(func_name, 2, order_func, deterministic=True)

        if not order_bys:
            return ""
        return "ORDER BY " + ",".join(order_bys)


class VersionedDatabaseMixin:
    VERSION = 6

    @property
    def _version(self):
        cursor = self.connection.execute("PRAGMA user_version;")
        for res in cursor:
            version = res[0]
            return version if version else None
        assert False

    def _set_version(self):
        if self._version is None:
            self.connection.execute(f"PRAGMA user_version = {self.VERSION};")
            return
        self._check_version()

    def _check_version(self):
        version = self._version
        if version is None or version == self.VERSION:
            return
        raise Exception(
            (
                "Version mismatch: current version for database index"
                " is {self.VERSION} and the database already has version"
                f" {version}"
            )
        )


class SqlDatabase(Database, VersionedDatabaseMixin):
    EXTENSION = ".db"

    def __init__(
        self,
        db_path,
        filters=None,
    ):
        self._cache_column_names = {}

        self.db_path = db_path
        self._filters = filters or []
        self._view = None
        self._connection = None

        self.dbkeys = EntriesLoader(self.connection).keys

    @property
    def view(self):
        if self._view is None:
            self._view = "entries"
            for f in self._filters:
                self._apply_filter(f)
            LOG.debug("DB %s %s", self.db_path, self.view)
        return self._view

    @property
    def connection(self):
        if self._connection is None:
            self._connection = Connection(self.db_path)
        return self._connection._conn

    def _apply_filter(self, filter: SqlFilter):
        # This method updates self.view with the additional filter

        old_view = self._view
        new_view = old_view + "_" + filter.h(parent_view=old_view)

        filter_statement = filter.filter_statement(self, new_view)

        statement = (
            f"CREATE TEMP VIEW IF NOT EXISTS {new_view} AS SELECT * "
            + f"FROM {old_view} {filter_statement};"
        )

        LOG.debug("%s", statement)
        for i in self.connection.execute(statement):
            LOG.error(str(i))  # Output of .execute should be empty

        self._view = new_view

    def filter(self, filter: SqlFilter):
        return self.__class__(
            self.db_path,
            filters=self._filters + [filter],
        )

    def load(self, iterator):
        with self.connection as connection:
            loader = EntriesLoader(connection)
            count = loader.load_iterator(iterator)
            self.dbkeys = loader.keys

            assert count >= 1, "No entry found."
            LOG.info("Added %d entries", count)

        return count

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

    def lookup_dicts(self, limit=None, offset=None, remove_none=True, with_parts=None):
        """
        Return entries dicts as they where inserted into the database.
        limit: Returns only "limit" entries (used for paging).
        offset: Skip the first "offset" entries (used for paging).
        """

        column_names = [k for k, v in self.dbkeys.items()]

        if with_parts is False:
            column_names = [k for k in column_names if k not in FILEPARTS_KEY_NAMES]

        entrynames = [dbname_to_entryname(k) for k in column_names]
        for tupl in self._execute_select(column_names, limit, offset):
            dic = {k: v for k, v in zip(entrynames, tupl)}

            if remove_none:
                dic = {k: v for k, v in dic.items() if v is not None}
            yield dic

    def _execute_select(self, column_names, limit=None, offset=None):
        names_str = ",".join([x for x in column_names]) if column_names else "*"
        limit_str = f" LIMIT {limit}" if limit is not None else ""
        offset_str = f" OFFSET {offset}" if offset is not None else ""

        statement = f"SELECT {names_str} FROM {self.view} {limit_str} {offset_str};"
        LOG.debug("%s", statement)

        for tupl in self.connection.execute(statement):
            yield tupl

    def count(self):
        statement = f"SELECT COUNT(*) FROM {self.view};"
        for result in self.connection.execute(statement):
            return result[0]
        assert False, statement  # Fail if result is empty.

    def duplicate_db(self, filename, **kwargs):
        new_db = SqlDatabase(db_path=filename)
        iterator = self.lookup_dicts()
        new_db.load(iterator)
        return new_db
