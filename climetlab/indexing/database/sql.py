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
import time
from threading import local

import numpy as np

import climetlab as cml
from climetlab.indexing.database.json import json_serialiser
from climetlab.loaders import build_remapping
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


def dump_sql(statement):
    statement = statement.replace(",", ", ")
    statement = statement.replace(";", " ;")
    statement = statement.replace("(", " (")
    lst = statement.split()
    lst = [
        "userorder_entries_...\n" if x.startswith("userorder_entries") else x
        for x in lst
    ]
    print(" ".join(lst))


def execute(connection, statement, *arg, **kwargs):
    if LOG.level == logging.DEBUG:
        assert False
        dump_sql(statement)

    delay = 1
    while delay < 30 * 60:  # max delay 30 min
        try:
            return connection.execute(statement, *arg, **kwargs)
        except sqlite3.OperationalError as e:
            if not str(e).endswith("database is locked"):
                raise e
            time.sleep(delay)
            dump_sql(statement)
            print(f"{e}. Retrying in {delay} seconds.")
            delay = delay * 1.5
    raise e  # noqa: F821


def entryname_to_dbname(n):
    n = dict(
        levellist="levelist",
        level="levelist",
        leveltype="levtype",
        variable="param",
        parameter="param",
        realization="number",
        realisation="number",
        klass="class",
    ).get(n, n)

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
        self.patch()
        self.keys = self.read_from_table()
        self.path_table = PathTable(connection)

    def patch(self):
        try:
            execute(
                self.connection,
                "ALTER TABLE entries RENAME COLUMN i_datetime TO i_valid_datetime;",
            )
        except sqlite3.OperationalError:
            pass

        try:
            execute(
                self.connection, "ALTER TABLE entries DROP COLUMN i_param_levelist;"
            )
        except sqlite3.OperationalError:
            pass

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
        cursor = execute(self.connection, f"PRAGMA table_info({self.table_name})")
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
            dbkey = self._build_dbkey(k, v)
            keys[dbkey.name] = dbkey

        assert keys, f"Cannot build from entry '{entry}'"
        LOG.debug(f"Created table {self} from entry {entry}.")
        columns_defs = ",".join([f"{v.name} {v.sql_type}" for k, v in keys.items()])
        statement = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({columns_defs});"
        execute(self.connection, statement)
        return self.read_from_table()

    def _add_column(self, k, v):
        dbkey = self._build_dbkey(k, v)
        statement = (
            f"ALTER TABLE {self.table_name} ADD COLUMN {dbkey.name} {dbkey.sql_type};"
        )
        LOG.debug("%s", statement)
        try:
            execute(self.connection, statement)
        except sqlite3.OperationalError:
            LOG.debug("Add column failed, this is expected because of concurency")
        self.keys[dbkey.name] = dbkey
        return self.keys

    def _build_dbkey(self, k, v):
        typ = type(v)
        klass = self.guess_key_type(typ, name=k)
        name = entryname_to_dbname(k)
        return klass(name)

    def load_iterator(self, iterator):
        paths_or_urls = set()

        count = 0
        for entry in iterator:
            if count == 0:
                self.keys = self.create_table_from_entry_if_needed(entry)

            for k, v in entry.items():
                dbname = entryname_to_dbname(k)
                if dbname not in self.keys:
                    LOG.debug(f"Inserting column in databse {k}, {dbname}")
                    self.keys = self._add_column(k, v)

            if "_path" in entry:
                paths_or_urls.add(entry["_path"])
            if "_url" in entry:
                paths_or_urls.add(entry["_url"])

            column_names = [k for k, v in self.keys.items()]
            statement = (
                f"INSERT INTO {self.table_name} ("
                + ",".join(column_names)
                + ") VALUES("
                + ",".join(["?"] * len(column_names))
                + ");"
            )
            values = [entry.get(dbname_to_entryname(k)) for k, v in self.keys.items()]
            execute(self.connection, statement, tuple(values))
            count += 1

        date = datetime.datetime.now().isoformat()
        for path in paths_or_urls:
            self.path_table.insert(path, date)

        return count

    def build_sql_indexes(self):
        indexed_columns = [k for k, v in self.keys.items() if k.startswith("i_")]
        indexed_columns += ["path"]

        pbar = tqdm(indexed_columns, desc="Building indexes")
        for n in pbar:
            pbar.set_description(f"Building index for {n}")
            execute(
                self.connection,
                f"CREATE INDEX IF NOT EXISTS {n}_index ON {self.table_name} ({n});",
            )

    def __str__(self):
        content = ",".join([k for k, v in self.keys.items()])
        return f"{self.__class__.__name__}({self.table_name},{content}"


class Connection(local):
    # Inheriting from threading.local allows one connection for each thread
    # __init__ is "called each time the local object is used in a separate thread".
    # https://github.com/python/cpython/blob/0346eddbe933b5f1f56151bdebf5bd49392bc275/Lib/_threading_local.py#L65
    def __init__(self, db_path):
        self._conn = sqlite3.connect(db_path)


class SqlFilter:
    def __init__(self, kwargs=None, remapping=None):
        self.kwargs = kwargs or {}
        self.remapping = build_remapping(remapping)

    def h(self, *args, **kwargs):
        m = hashlib.md5()
        m.update(str(args).encode("utf-8"))
        m.update(str(kwargs).encode("utf-8"))
        m.update(str(self.remapping.as_dict()).encode("utf-8"))
        m.update(str(self.__class__.__name__).encode("utf-8"))
        m.update(
            json.dumps(self.kwargs, sort_keys=True, default=json_serialiser).encode(
                "utf-8"
            )
        )
        return m.hexdigest()

    def __str__(self):
        return f"{self.__class__.__name__}({self.kwargs})"

    @property
    def is_empty(self):
        return not self.kwargs

    def create_new_view(self, db, view):
        new_view = "entries_" + self.h(parent_view=view)
        assert new_view != view
        view_statement = self.create_view_statement(
            db, old_view=view, new_view=new_view
        )
        if not view_statement:
            # nothing to do
            return view

        LOG.debug("%s", view_statement)
        for i in execute(db.connection, view_statement):
            LOG.error(str(i))
        return new_view


class SqlSelection(SqlFilter):
    def create_view_statement(self, db, old_view, new_view):
        conditions = []
        for k, v in self.kwargs.items():
            if v is None or v is cml.ALL:
                continue

            name = entryname_to_dbname(k)
            dbkey = db.dbkeys[name]

            if not isinstance(v, (list, tuple)):
                v = [v]

            v = [dbkey.cast(x) for x in v]
            v = ["'" + str(x) + "'" for x in v]

            conditions.append(f"{name} IN ({', '.join(v)})")

        if not conditions:
            return None

        assert new_view != old_view
        return (
            f"CREATE TEMP VIEW IF NOT EXISTS {new_view} AS SELECT * "
            + f"FROM {old_view} WHERE "
            + " AND ".join(conditions)
            + ";"
        )


class SqlRemapping(SqlFilter):
    def create_view_statement(self, db, old_view, new_view):
        class SqlCustomJoiner:
            def format_name(self, x):
                name = entryname_to_dbname(x)
                return f"COALESCE({name},'')"

            def format_string(self, name):
                if not name:
                    return name
                return "'" + str(name) + "'"

            def join(self, lst):
                lst = [_ for _ in lst if len(_)]
                assert len(lst) > 0, lst
                return " || ".join(lst)

        sql_concatenations = []
        for k, v in self.remapping.remapping.items():
            joiner = SqlCustomJoiner()
            alias = entryname_to_dbname(k)
            expr = self.remapping.substitute(k, joiner)
            sql_concatenations.append(f"TRIM({expr},'_') AS {alias}")

        select = ", ".join(sql_concatenations)

        if not sql_concatenations:
            return None

        assert new_view != old_view
        return (
            f"CREATE TEMP VIEW IF NOT EXISTS {new_view} AS SELECT *, {select} "
            f"FROM {old_view};"
        )


class SqlOrder(SqlFilter):
    def merge(self, *others):
        orders = reversed([self, *others])

        kwargs = {}
        for o in orders:
            for k, v in o.kwargs.items():
                if k not in kwargs:
                    kwargs[k] = v

        return SqlOrder(kwargs)

    def create_view_statement(self, db, old_view, new_view):
        func_name = "userorder_" + new_view

        order_bys = []
        dict_of_dicts = {}

        for k, v in self.kwargs.items():
            name = entryname_to_dbname(k)

            dbkey = db.dbkeys.get(name, StrDBKey(name))

            if v == "ascending" or v is None:
                order_bys.append(name + " ASC")
                continue
            if v == "descending":
                order_bys.append(name + " DESC")
                continue
            if isinstance(v, (list, tuple)):
                v = [dbkey.cast(x) for x in v]
                dict_of_dicts[name] = dict(zip(v, range(len(v))))
                order_bys.append(func_name + "(" + "'" + name + "'" + ", " + name + ")")
                continue

            raise ValueError(f"{k},{v}, {type(v)}")

        if not order_bys:
            return None

        if dict_of_dicts:

            def order_func(k, v):
                return dict_of_dicts[k][v]

            if LOG.level == logging.DEBUG:
                sqlite3.enable_callback_tracebacks(True)
            db.connection.create_function(func_name, 2, order_func, deterministic=True)

        assert new_view != old_view
        return (
            f"CREATE TEMP VIEW IF NOT EXISTS {new_view} AS SELECT * "
            + f"FROM {old_view} ORDER BY "
            + ",".join(order_bys)
            + ";"
        )


class VersionedDatabaseMixin:
    VERSION = 6

    @property
    def _version(self):
        cursor = execute(self.connection, "PRAGMA user_version;")
        for res in cursor:
            version = res[0]
            return version if version else None
        assert False

    def _set_version(self):
        if self._version is None:
            execute(self.connection, f"PRAGMA user_version = {self.VERSION};")
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


class PathTable:
    table_name = "paths"

    def __init__(self, connection):
        self.connection = connection
        self.ensure_table()

    def ensure_table(self):
        statement = f"CREATE TABLE IF NOT EXISTS {self.table_name} (key TEXT PRIMARY KEY, date TEXT);"
        for i in execute(self.connection, statement):
            LOG.error(str(i))  # Output of .execute should be empty

    def insert(self, key, date):
        statement = f"""INSERT INTO {self.table_name} (key, date) VALUES(?,?);"""
        LOG.debug("%s", statement)
        execute(self.connection, statement, (key, date))

    def get_date(self, key):
        statement = f"""SELECT * FROM {self.table_name} WHERE key="{key}";"""
        LOG.debug("%s", statement)
        for key, date in execute(self.connection, statement):
            return date
        return None


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

    def __str__(self):
        return f"{self.__class__.__name__}({self.db_path},filters=[{','.join([str(_) for _ in self._filters])}])"

    def build_indexes(self):
        EntriesLoader(self.connection).build_sql_indexes()

    @property
    def view(self):
        if self._view is None:
            self._view = "entries"
            for f in self._filters:
                self._view = f.create_new_view(self, self._view)
            LOG.debug("DB %s %s", self.db_path, self._view)
        return self._view

    @property
    def connection(self):
        if self._connection is None:
            self._connection = Connection(self.db_path)
        return self._connection._conn

    def unique_values(self, *coords, remapping=None, progress_bar=True):
        """
        Given a list of metadata attributes, such as date, param, levels,
        returns the list of unique values for each attributes
        """

        remapping = build_remapping(remapping)
        with self.connection as con:
            view = self.view
            # orders = [f for f in self._filters if isinstance(f, SqlOrder)]
            # if orders:
            #     order = orders[0].merge(*orders)
            #     view = order.create_new_view(self, view)

            results = {}
            for c in coords:
                column = entryname_to_dbname(c)
                values = [
                    v[0] for v in execute(con, f"SELECT DISTINCT {column} FROM {view};")
                ]
                LOG.debug("Reordered values for {column}", column, values)
                results[column] = values

        return results

    def filter(self, filter: SqlFilter):
        return self.__class__(
            self.db_path,
            filters=self._filters + [filter],
        )

    def already_loaded(self, path_or_url, owner):
        with self.connection as connection:
            date = PathTable(connection).get_date(path_or_url)
            return date is not None

    def load_iterator(self, iterator):
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

        for tupl in execute(self.connection, statement):
            yield tupl

    def count(self):
        statement = f"SELECT COUNT(*) FROM {self.view};"
        for result in execute(self.connection, statement):
            return result[0]
        assert False, statement  # Fail if result is empty.

    def duplicate_db(self, filename, **kwargs):
        new_db = SqlDatabase(db_path=filename)
        iterator = self.lookup_dicts()
        new_db.load(iterator)
        return new_db
