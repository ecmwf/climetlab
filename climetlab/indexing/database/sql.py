# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import datetime
import logging
import os
import sqlite3
from collections import defaultdict
from threading import local

import numpy as np

import climetlab as cml
from climetlab.core.index import (
    Order,
    OrderBase,
    OrderOrSelection,
    Selection,
    SelectionBase,
)
from climetlab.utils import tqdm
from climetlab.utils.parts import Part

from . import (
    FILEPARTS_KEY_NAMES,
    MORE_KEY_NAMES,
    STATISTICS_KEY_NAMES,
    Database,
    FloatDBKey,
    IntDBKey,
    StrDBKey,
)

LOG = logging.getLogger(__name__)


def entryname_to_dbname(n):
    def add_mars(x):
        return "mars_" + x

    def remove_first_underscore(x):
        assert x[0] == "_", x
        return x[1:]

    if n in FILEPARTS_KEY_NAMES:
        return remove_first_underscore(n)
    if n in MORE_KEY_NAMES:
        return remove_first_underscore(n)
    if n in STATISTICS_KEY_NAMES:
        return n
    return add_mars(n)


def dbname_to_entryname(n):
    if n.startswith("mars_"):
        return n[5:]
    if "_" + n in FILEPARTS_KEY_NAMES:
        return "_" + n
    if "_" + n in MORE_KEY_NAMES:
        return "_" + n
    return n


class EntriesLoader:
    table_name = "entries"

    KEY_TYPES = {
        "TEXT": StrDBKey,
        "FLOAT": FloatDBKey,
        "INTEGER": IntDBKey,
        str: StrDBKey,
        float: FloatDBKey,
        np.float64: FloatDBKey,
        np.float32: FloatDBKey,
        int: IntDBKey,
        datetime.datetime: StrDBKey,
    }

    def __init__(self, connection):
        self.connection = connection
        self.keys = {}
        self.build()

    def __str__(self):
        content = ",".join([k for k, v in self.keys.items()])
        return f"{self.__class__}({self.table_name},{content}"

    def build(self):
        cursor = self.connection.execute(f"PRAGMA table_info({self.table_name})")
        for x in cursor.fetchall():
            name = x[1]
            typ = x[2]
            klass = self.KEY_TYPES[typ]
            self.keys[name] = klass(name)

        if self.keys:
            return self.keys

        LOG.debug(f"Table {self.table_name} does not exist.")
        return None

    def create_table_from_entry_if_needed(self, entry):
        keys = {}
        for k, v in entry.items():
            typ = type(v)
            if typ not in self.KEY_TYPES:
                raise ValueError(f"Unknown type '{typ}' for key '{k}'.")
            klass = self.KEY_TYPES[typ]
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
            self.keys = self.create_table_from_entry_if_needed(entry)

            if count == 0:
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

        return self.keys, count

    def build_sql_indexes(self):
        indexed_columns = [k for k, v in self.keys.items() if k.startswith("mars_")]
        indexed_columns += ["path"]

        pbar = tqdm(indexed_columns, desc="Building indexes")
        for n in pbar:
            pbar.set_description(f"Building index for {n}")
            self.connection.execute(
                f"CREATE INDEX IF NOT EXISTS {n}_index ON {self.table_name} ({n});"
            )


def _list_all_tables(connection):
    statement = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor = connection.execute(statement)
    return [r[0] for r in cursor]


class CoordTable:
    def __init__(self, key, connection, create_if_not_exists=False):
        self.connection = connection
        self.key = key
        self.table_name = "coords_" + self.key
        if create_if_not_exists:
            self.create_table_if_not_exist()
        self.dic = self.read_table()

    def create_table_if_not_exist(self):
        create_statement = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
            key   INTEGER PRIMARY KEY,
            value TEXT
            );"""
        LOG.debug("%s", create_statement)
        self.connection.execute(create_statement)
        assert self._table_exists()

    def _table_exists(self):
        return self.table_name in _list_all_tables(self.connection)

    def read_table(self):
        if not self._table_exists():
            raise CoordTableDoesNotExist()

        statement = f"SELECT key,value FROM {self.table_name}; "
        LOG.debug("%s", statement)
        return {k: v for k, v in self.connection.execute(statement)}

    def append(self, value):
        value = str(value)

        if value in self.dic.values():
            return  # already in the table

        self.create_table_if_not_exist()

        statement = f"INSERT INTO {self.table_name} (value) VALUES(?); "
        LOG.debug("%s", statement)
        self.connection.execute(statement, [value])

        statement = f"SELECT key FROM {self.table_name} WHERE value='{value}'; "
        LOG.debug("%s", statement)
        keys = []
        for key in self.connection.execute(statement):
            keys.append(key)
        assert len(keys) == 1
        self.dic[key[0]] = value

    def is_empty(self):
        return len(self.dic) > 0

    def __len__(self):
        return len(self.dic)

    def items(self):
        return self.dic.items()

    def keys(self):
        return self.dic.keys()

    def __str__(self):
        typ = ""
        if self.dic:
            first = self.dic[list(self.dic.keys())[0]]
            if not isinstance(first, str):
                typ = f" ({type(first)})"
        return f"{self.key}{typ}={'/'.join([str(v) for v in self.dic.values()])}"


class CoordTableDoesNotExist(Exception):
    pass


class CoordTables:
    def __init__(self, connection):
        self.connection = connection
        self.dic = {}

        for table in _list_all_tables(self.connection):
            if not table.startswith("coords_"):
                continue
            key = table[len("coords_") :]
            self.dic[key] = CoordTable(key, self.connection)

    def __getitem__(self, key):
        if key not in self.dic:
            self.dic[key] = CoordTable(key, self.connection, create_if_not_exists=True)
        return self.dic[key]

    def update_with_entry(self, entry):
        for n in [k.name for k in GRIB_KEYS] + ["md5_grid_section"] + ["_path"]:
            v = entry.get(n)
            if v is None:
                continue
            self[n].append(v)

    def __str__(self):
        return "Coords:" + "\n".join([str(v) for k, v in self.dic.items()])

    def __len__(self):
        return len(self.dic)

    def items(self):
        return self.dic.items()

    def keys(self):
        return self.dic.keys()


class Connection(local):
    # Inheriting from threading.local allows one connection for each thread
    # __init__ is "called each time the local object is used in a separate thread".
    # https://github.com/python/cpython/blob/0346eddbe933b5f1f56151bdebf5bd49392bc275/Lib/_threading_local.py#L65
    def __init__(self, db_path):
        self._conn = sqlite3.connect(db_path)


class SqlSelection(SelectionBase):
    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


class SqlOrder(OrderBase):
    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_actions(self, kwargs):
        return

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

            print("** CREATING on", db.connection, func_name)
            db.connection.create_function(func_name, 2, order_func, deterministic=True)

        if not order_bys:
            return ""
        return "ORDER BY " + ",".join(order_bys)


class SqlDatabase(Database):
    VERSION = 5
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
            print("----CONNECTION TO ", self.db_path, self._connection._conn)
        return self._connection._conn

    def _apply_filter(self, filter: OrderOrSelection):
        # This method updates self.view with the additional filter

        old_view = self._view
        new_view = old_view + "_" + filter.h(parent_view=old_view)[:3]

        filter_statement = filter.filter_statement(self, new_view)

        statement = (
            f"CREATE TEMP VIEW IF NOT EXISTS {new_view} AS SELECT * "
            + f"FROM {old_view} {filter_statement};"
        )

        LOG.debug("%s", statement)
        for i in self.connection.execute(statement):
            LOG.error(str(i))  # Output of .execute should be empty

        self._view = new_view

    def filter(self, filter: OrderOrSelection):
        return self.__class__(
            self.db_path,
            filters=self._filters + [filter],
        )

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

    @property
    def key_names(self):
        return [dbname_to_entryname(k) for k, v in self.dbkeys.items()]

    @property
    def column_names(self):
        return [k for k, v in self.dbkeys.items()]

    def load(self, iterator):
        with self.connection as connection:
            loader = EntriesLoader(connection)
            self.dbkeys, count = loader.load_iterator(iterator)

            assert count >= 1, "No entry found."
            LOG.info("Added %d entries", count)

        return count

    def _conditions(self, selection):
        if selection is None:
            return ""
        conditions = []
        for k, b in selection.kwargs.items():
            if b is None or b == cml.ALL:
                continue

            dbkey = self.dbkeys[k]

            if isinstance(b, (list, tuple)):
                # if len(b) == 1:
                #    conditions.append(f"{dbkey.name_in_db}='{b[0]}'")
                #    continue
                w = ",".join([dbkey.to_sql_value(x) for x in b])
                conditions.append(f"{dbkey.name_in_db} IN ({w})")
                continue

            conditions.append(f"{dbkey.name_in_db}='{b}'")

        if not conditions:
            return ""
        return " WHERE " + " AND ".join(conditions)

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

    def lookup_dicts(
        self,
        # keys=None,
        limit=None,
        offset=None,
        remove_none=True,
        with_parts=None,
    ):
        """
        From a list of keys, return dicts with these columns of the database.
        limit: Returns only "limit" entries (used for paging).
        offset: Skip the first "offset" entries (used for paging).
        """

        column_names = self.column_names
        names = self.key_names
        # if keys is None:
        #    keys = [v.name for k,v in self.dbkeys.items()]
        #    if with_parts is None:
        #        with_parts = True

        # if not isinstance(keys, (list, tuple)):
        #    keys = [keys]

        # if with_parts:
        #    keys = FILEPARTS_KEY_NAMES + keys

        # dbkeys = [self.dbkeys[name] for name in keys]

        # column_names = [k.name_in_db for k in dbkeys]
        # names = [k.name for k in dbkeys]
        for tupl in self._execute_select(column_names, limit, offset):
            dic = {k: v for k, v in zip(names, tupl)}

            if remove_none:
                dic = {k: v for k, v in dic.items() if v is not None}
            yield dic

    def _execute_select(self, column_names, limit=None, offset=None):
        names_str = ",".join([x for x in column_names]) if column_names else "*"
        limit_str = f" LIMIT {limit}" if limit is not None else ""
        offset_str = f" OFFSET {offset}" if offset is not None else ""

        statement = f"SELECT {names_str} FROM {self.view} {limit_str} {offset_str};"
        LOG.debug("%s", statement)

        print(self.connection)
        for tupl in self.connection.execute(statement):
            yield tupl

    def _find_all_coords_dict(self):
        raise NotImplementedError("wip")
        # start-of: This is just an optimisation for speed.
        if all([isinstance(f, Order) for f in self._filters]):
            # if there is a Selection filter, it may remove some keys
            # by selecting values on some other keys.
            # In such case, we cannot rely on the coords tables created
            # for the whole dataset.
            # For instance doing .sel(param='2t') will remove some keys
            # for step that had been inserted by param='tp'.
            return self._find_all_coords_dict_from_coords_tables()
        # end-of: This is just an optimisation for speed.

        values = defaultdict(list)
        i_names = self._columns_names("i", remove_prefix=False)
        names = self._columns_names("i", remove_prefix=True)
        for tupl in self._execute_select(i_names):
            for k, v in zip(names, tupl):
                if v in values[k]:
                    continue
                values[k].append(v)

        return values

    def _find_all_coords_dict_from_coords_tables(self):
        raise NotImplementedError("wip")
        # coords_tables = CoordTables(self.connection)
        # keys = list(coords_tables.keys())
        # keys = [k for k in keys if k in GRIB_KEYS_NAMES]

        # for f in self._filters:
        #     firsts = list(f.keys())
        #     keys = firsts + [k for k in keys if k not in firsts]

        # coords = {k: coords_tables[k].dic.values() for k in keys}

        # for f in self._filters:
        #     coords = {k: f.filter_values(k, v) for k, v in coords.items()}

        # return coords

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

    def normalize_datetime(self, value):
        return value
