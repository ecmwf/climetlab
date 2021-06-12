# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

"""

Internally, CliMetLab cache is managed by the module `climetlab.core.cache`, it relies on a sqlite database. The :py:func:`cache_file` function provide a unique path for a given couple (`owner`, `args`). The calling code is responsible for checking if the file exists and decide to read it or create it.

"""  # noqa: E501

import datetime
import hashlib
import json
import logging
import os
import shutil
import sqlite3
import tempfile
import threading

from climetlab.utils import bytes_to_string
from climetlab.utils.html import css

from .settings import SETTINGS

VERSION = 1
CACHE_DB = f"cache-{VERSION}.db"

LOG = logging.getLogger(__name__)


LOCK = threading.Lock()


class Connection(threading.local):
    def __init__(self):
        pass

    @property
    def db(self):
        if not hasattr(self, "_db"):
            self._db = None
        return self._db

    @db.setter
    def db(self, db):
        self._db = db

    def __enter__(self):
        if self.db is None:
            cache_dir = SETTINGS.get("cache-directory")
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir, exist_ok=True)
            cache_db = os.path.join(cache_dir, CACHE_DB)
            self.db = sqlite3.connect(cache_db)
            # So we can use rows as dictionaries
            self.db.row_factory = sqlite3.Row

            # If you change the schema, change VERSION above
            self.db.execute(
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
        return self.db.__enter__()

    def __exit__(self, *args, **kwargs):
        return self.db.__exit__(*args, **kwargs)


connection = Connection()


def _settings_changed():
    """Need to be called when the settings has been changed to update the connection to the cache database."""
    if connection.db is not None:
        connection.db.close()
    connection.db = None
    _check_cache_size()


SETTINGS.on_change(_settings_changed)


def latest_date():
    """Returns the latest date to be used when purging the cache.
    So we do not purge files being downloaded."""
    with connection as db:
        latest = db.execute(
            "SELECT MIN(creation_date) FROM cache WHERE size IS NULL"
        ).fetchone()[0]
        if latest is None:
            latest = db.execute("SELECT MAX(creation_date) FROM cache").fetchone()[0]
        if latest is None:
            latest = datetime.datetime.utcnow()
        return latest


def purge_cache(owner):
    with connection as db:
        db.execute("DELETE FROM cache WHERE owner=?", (owner,))
        db.commit()


def get_cached_files():
    _update_cache(True)
    with connection as db:
        for n in db.execute("SELECT * FROM cache").fetchall():
            n = dict(n)
            n["args"] = json.loads(n["args"])
            yield n


def _update_cache(clean=False):
    """Update cache size and size of each file in the database ."""
    with connection as db:
        update = []
        commit = False
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
                if clean:
                    db.execute("DELETE from cache WHERE path=?", (path,))
                    commit = True

        if update:
            db.executemany("UPDATE cache SET size=?, type=? WHERE path=?", update)

        if update or commit:
            db.commit()


def _find_orphans():
    top = SETTINGS.get("cache-directory")
    with connection as db:
        for name in os.listdir(top):
            if name == CACHE_DB:
                continue

            full = os.path.join(top, name)
            count = db.execute(
                "SELECT count(*) FROM cache WHERE path=?", (full,)
            ).fetchone()[0]

            if count == 0:
                LOG.warning(f"cache orphan found: {full}")
                _register_cache_file(
                    full,
                    "orphans",
                    None,
                )


def _delete_entry(db, top, entry):
    path, size = entry["path"], entry["size"]
    assert path.startswith(top), (path, top)
    if not os.path.exists(path):
        LOG.warning(f"cache file lost: {path}")
        with connection as db:
            db.execute("DELETE FROM cache WHERE path=?", (path,))
        return 0
    delete = path + ".delete"
    os.rename(path, delete)
    LOG.warning(f"CliMetLab cache: deleting {path} ({bytes_to_string(size)})")
    if os.path.isdir(delete):
        shutil.rmtree(delete)
    else:
        os.unlink(delete)
    db.execute("DELETE FROM cache WHERE path=?", (path,))
    return size


def decache(bytes):
    _find_orphans()
    _update_cache(clean=True)

    if bytes <= 0:
        return 0

    LOG.warning("CliMetLab cache: trying to free %s", bytes_to_string(bytes))

    total = 0
    top = SETTINGS.get("cache-directory")
    with connection as db:

        latest = latest_date()

        try:
            # Remove all orphans
            for stmt in (
                "SELECT * FROM cache WHERE owner='orphans' AND creation_date < ?",
                "SELECT * FROM cache WHERE creation_date < ? ORDER BY last_access DESC",
            ):
                for entry in db.execute(stmt, (latest,)):
                    total += _delete_entry(db, top, entry)
                    if total >= bytes:
                        LOG.warning(
                            "CliMetLab cache: freed %s from cache",
                            bytes_to_string(bytes),
                        )
                        return total
        finally:
            db.commit()

    LOG.warning("CliMetLab cache: could not free %s", bytes_to_string(bytes))


def _register_cache_file(path, owner, args):
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

    with connection as db:

        now = datetime.datetime.utcnow()

        args = json.dumps(args)

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


def _update_hash(m, x):
    """Recursively call the _update_hash() on `m` with the values (and keys) given in `x`.

    Parameters
    ----------
    m : dict
        Object with a _update_hash method.
    x : list or dict or any
        values to send as parameter to m._update_hash()
    """
    if isinstance(x, (list, tuple)):
        for y in x:
            _update_hash(m, y)
        return

    if isinstance(x, dict):
        for k, v in sorted(x.items()):
            _update_hash(m, k)
            _update_hash(m, v)
        return

    m._update_hash(str(x).encode("utf-8"))


def cache_size():
    with connection as db:
        size = db.execute("SELECT SUM(size) FROM cache").fetchone()[0]
        if size is None:
            size = 0
        return size


def _check_cache_size():
    maximum = SETTINGS.as_bytes("maximum-cache-size")
    size = cache_size()
    if size > maximum:
        decache(size - maximum)


def cache_file(owner: str, create, args, extension: str = ".cache"):
    """Creates a cache file in the climetlab cache-directory (defined in the :py:class:`Settings`).
    Uses :py:func:`_register_cache_file()`

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
    _update_hash(m, owner)
    _update_hash(m, args)
    path = "%s/%s-%s%s" % (
        SETTINGS.get("cache-directory"),
        owner.lower(),
        m.hexdigest(),
        extension,
    )

    _register_cache_file(path, owner, args)

    if not os.path.exists(path):

        _check_cache_size()

        create(path + ".tmp", args)
        os.rename(path + ".tmp", path)
        _update_cache()

        _check_cache_size()

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

        _update_cache(True)

        html = [css("table")]
        with connection as db:
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
