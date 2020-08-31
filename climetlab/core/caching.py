# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import tempfile
import hashlib
import datetime
import sqlite3
import json

# import threading

from .settings import SETTINGS


_connection = None


def connection():
    global _connection
    if _connection is None:
        cache_dir = SETTINGS.get("cache_directory")
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
        cache_db = os.path.join(cache_dir, "cache.db")
        _connection = sqlite3.connect(cache_db)
        # So we can use rows as dictionaries
        _connection.row_factory = sqlite3.Row

        _connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                    path text PRIMARY KEY,
                    owner text NOT NULL,
                    args text NOT NULL,
                    creation_date text NOT NULL,
                    remote_date text, -- TODO expire URLs
                    remote_tag text,  -- TODO expire URLs
                    last_access text,
                    expires int,
                    accesses int,
                    size int);"""
        )

        update = []
        for n in _connection.execute("select path from cache where size is null"):
            try:
                update.append((os.path.getsize(n[0]), n[0]))
            except Exception:
                pass

        if update:
            _connection.executemany("update cache set size=? where path=?", update)
            _connection.commit()

    return _connection


def settings_changed():
    global _connection
    if _connection is not None:
        _connection.close()
    _connection = None


SETTINGS.on_change(settings_changed)


def register_cache_file(path, owner, args):

    db = connection()

    now = datetime.datetime.utcnow()

    try:
        db.execute(
            """
            INSERT INTO cache(
                            path,
                            owner,
                            args,
                            creation_date,
                            last_access,
                            accesses)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(path)
            DO UPDATE SET
                accesses=accesses+1,
                last_access=?""",
            (path, owner, json.dumps(args), now, now, 1, now),
        )
    except sqlite3.OperationalError:
        # Older version of sqlite?
        try:
            db.execute(
                """
                INSERT INTO cache(
                                path,
                                owner,
                                args,
                                creation_date,
                                last_access,
                                accesses)
                VALUES(?,?,?,?,?,?)""",
                (path, owner, json.dumps(args), now, now, 1)
            )
        except sqlite3.IntegrityError:
            db.execute(
                """
                UPDATE cache SET
                    accesses=accesses+1,
                    last_access=?""",
                (now,),
            )

    # print(list(c))

    db.commit()


def update(m, x):
    if isinstance(x, (list, tuple)):
        for y in x:
            update(m, y)
        return

    if isinstance(x, dict):
        for k, v in sorted(x.items()):
            update(m, k)
            update(m, v)
        return

    m.update(str(x).encode("utf-8"))


def class_full_name(o):
    if o.__module__ is None:
        return o.__name__
    return o.__module__ + "." + o.__name__


def cache_file(owner: type, *args, extension: str = ".cache"):
    m = hashlib.sha256()
    klass = class_full_name(owner)
    update(m, klass)
    update(m, args)
    path = "%s/%s-%s%s" % (
        SETTINGS.get("cache_directory"),
        owner.__name__.lower(),
        m.hexdigest(),
        extension,
    )
    register_cache_file(path, klass, args)
    return path


class TmpFile:
    def __init__(self, path):
        self.path = path

    def __del__(self):
        os.unlink(self.path)


def temp_file(extension=".tmp"):
    fd, path = tempfile.mkstemp(suffix=extension)
    os.close(fd)
    return TmpFile(path)


class Cache:
    def _repr_html_(self):
        html = []
        with connection() as db:
            for n in db.execute("select * from cache"):
                html.append("<table>")
                for k in n.keys():
                    html.append("<td><td>%s</td><td>%s</td></tr>" % (k, n[k]))
                html.append("</table>")
        return "".join(html)


CACHE = Cache()
