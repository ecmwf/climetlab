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



    return _connection


def settings_changed():
    global _connection
    if _connection is not None:
        _connection.close()
    _connection = None


SETTINGS.on_change(settings_changed)


def update_cache():

    with connection() as db:
        update = []
        for n in db.execute("select path from cache where size is null"):
            try:
                update.append((os.path.getsize(n[0]), n[0]))
            except Exception:
                pass

        if update:
            db.executemany("update cache set size=? where path=?", update)
            db.commit()

def register_cache_file(path, owner, args):

    db = connection()

    now = datetime.datetime.utcnow()

    args = json.dumps(args, indent=4)

    db.execute(
                """
                UPDATE cache SET
                    accesses=accesses+1,
                    last_access=?
                WHERE path=?
                """,
                (now, path))

    changes = db.execute("SELECT changes()").fetchone()[0]

    if not changes:

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
            (path, owner, args, now, now, 1),
        )

    db.commit()
    return not changes


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

    if register_cache_file(path, klass, args):
        update_cache()

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

        update_cache()

        html = []
        with connection() as db:
            for n in db.execute("select * from cache"):
                html.append("<table>")
                html.append("<td><td colspan='2'>%s</td></tr>" % (n["path"],))

                for k in [x for x in n.keys() if x != "path"]:
                    html.append("<td><td>%s</td><td>%s</td></tr>" % (k, n[k]))
                html.append("</table>")
                html.append("<br>")
        return "".join(html)


CACHE = Cache()
