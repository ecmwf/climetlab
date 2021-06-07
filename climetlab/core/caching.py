# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

"""

CliMetLab cache is managed by the module `climetlab.core.cache`, it relies on a sqlite database. The :py:func:`cache_file` function provide a unique path for a given couple (`owner`, `args`). The calling code is responsible for checking if the file exists and decide to read it or create it.

.. todo::

    Implement cache invalidation, and checking if there is enough space on disk.

"""  # noqa: E501

import datetime
import hashlib
import json
import os
import sqlite3
import tempfile
import threading

from climetlab.decorators import locked
from climetlab.utils import bytes_to_string
from climetlab.utils.html import css

from .settings import SETTINGS

_connection = threading.local()


@locked
def connection():
    """Get a connection to the sqlite cache database. The database is accessible through the "db" member.

    Returns:
    -------
    connection: obj
        Connection object, has a db member : _connection.db.
    """

    global _connection
    if not hasattr(_connection, "db") or _connection.db is None:
        cache_dir = SETTINGS.get("cache-directory")
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        cache_db = os.path.join(cache_dir, "cache.db")
        _connection.db = sqlite3.connect(cache_db)
        # So we can use rows as dictionaries
        _connection.db.row_factory = sqlite3.Row

        _connection.db.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                    path          TEXT PRIMARY KEY,
                    owner         TEXT NOT NULL,
                    args          TEXT NOT NULL,
                    creation_date TEXT NOT NULL,
                    flags         INTEGER DEFAULT 0,
                    remote_date   TEXT, -- TODO expire URLs
                    remote_tag    TEXT, -- TODO expire URLs
                    last_access   TEXT,
                    type          TEXT,
                    parent        TEXT,
                    extra         TEXT,
                    expires       INTEGER,
                    accesses      INTEGER,
                    size          INTEGER);"""
        )

    return _connection.db


@locked
def settings_changed():
    """Need to be called when the settings has been changed to update the connection to the cache database."""
    global _connection
    if hasattr(_connection, "db") and _connection.db is not None:
        _connection.db.close()
    _connection.db = None


SETTINGS.on_change(settings_changed)


@locked
def update_cache():
    """Update cache size and size of each file in the database ."""
    with connection() as db:
        update = []
        for n in db.execute("SELECT path FROM cache WHERE size IS NULL"):
            try:
                path = n[0]
                if os.path.isdir(path):
                    kind = "directory"
                    size = 0
                    for root, _, files in os.walk(path):
                        for f in files:
                            size += os.path.getsize(os.path.join(root, f))
                else:
                    kind = "file"
                    size = os.path.getsize(path)
                update.append((size, kind, path))
            except Exception:
                pass

        if update:
            db.executemany("UPDATE cache SET size=?, type=? WHERE path=?", update)
            db.commit()


def register_cache_file(path, owner, args):
    """Register a file in the cache

    Parameters
    ----------
    path : str
        Cache file to register
    owner : str
        Owner of the cache file (generally a source or a dataset)
    args : dict
        Dictionary to save with the file in the database, as json string.

    Returns
    -------
    changes :
        None or False if database does not need to be updated. TODO: clarify.
    """

    db = connection()

    now = datetime.datetime.utcnow()

    args = json.dumps(args, indent=4)

    db.execute(
        """
        UPDATE cache
        SET accesses    = accesses + 1,
            last_access = ?
        WHERE path=?""",
        (now, path),
    )

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


def update(m, x):
    """Recursively call the update() on `m` with the values (and keys) given in `x`.

    Parameters
    ----------
    m : dict
        Object with a update method.
    x : list or dict or any
        values to send as parameter to m.update()
    """
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


@locked
def cache_file(owner: str, *args, extension: str = ".cache"):
    """Creates a cache file in the climetlab cache-directory (defined in the :py:class:`Settings`).
    Uses :py:func:`register_cache_file()`

    Parameters
    ----------
    owner : str
        The owner of the cache file is generally the name of the source that generated the cache.
    extension : str, optional
        Extension filename (such as ".nc" for NetCDF, etc.), by default ".cache"

    Returns
    -------
    path : str
        Full path to the cache file.
    """

    m = hashlib.sha256()
    update(m, owner)
    update(m, args)
    path = "%s/%s-%s%s" % (
        SETTINGS.get("cache-directory"),
        owner.lower(),
        m.hexdigest(),
        extension,
    )

    if register_cache_file(path, owner, args):
        update_cache()

    return path


class TmpFile:
    """The TmpFile objets are designed to be used for temporary files. It ensures that the file is unlinked when the object is out-of-scope (with __del__).

    Parameters
    ----------
    path : str
        Actual path of the file.
    """  # noqa: E501

    def __init__(self, path: str):
        self.path = path

    def __del__(self):
        os.unlink(self.path)


@locked
def temp_file(extension=".tmp") -> TmpFile:
    """Create a temporary file with the given extension .

    Parameters
    ----------
    extension : str, optional
        By default ".tmp"

    Returns
    -------
    TmpFile
    """

    fd, path = tempfile.mkstemp(suffix=extension)
    os.close(fd)
    return TmpFile(path)


class Cache:
    """Cache object providing a nice representation of the cache state."""

    def _repr_html_(self):
        """Return a html representation of the cache .

        Returns
        -------
        str
            HTML status of the cache.
        """

        update_cache()

        html = [css("table")]
        with connection() as db:
            for n in db.execute("SELECT * FROM cache"):
                html.append("<table class='climetlab'>")
                html.append("<td><td colspan='2'>%s</td></tr>" % (n["path"],))

                for k in [x for x in n.keys() if x != "path"]:
                    v = bytes_to_string(n[k]) if k == "size" else n[k]
                    html.append("<td><td>%s</td><td>%s</td></tr>" % (k, v))
                html.append("</table>")
                html.append("<br>")
        return "".join(html)


CACHE = Cache()
