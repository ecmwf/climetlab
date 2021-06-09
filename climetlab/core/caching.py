# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

"""


CliMetLab cache configuration is managed through the CliMetLab :doc:`settings`.

The **cache location** is defined by `cache‑directory`.
This cache location does not matter when you are using a unique disk (this is the case for most laptops).
Linux system are different, the default location is assigned by the system for temporary files. If this default location is ``/tmp`` and if ``/tmp`` is mounted separately, it may have size to small for the data you intent to download.
Changing the cache location is detailed in the :doc:`settings` documentation.

.. todo::

    Implement cache invalidation, and checking if there is enough space on disk.

The **cache-minimum-disk-space** option ensures that CliMetLab does not fill your disk.
Its values sets the minimum disk space that must be left on the filesystem.
When the disk space goes below this limit, CliMetLab triggers its cache cleaning mechanism before downloading additional data.
The value of cache-minimum-disk-space can be absolute (such as "10G", "10M", "1K") or relative (such as "10%").

The **cache-maximum-size** option ensures that CliMetLab does not use to much disk space.
Its value sets the maximum disk space used by CliMetLab cache.
When CliMetLab cache disk usage goes above this limit, CliMetLab triggers its cache cleaning mechanism  before downloading additional data.
The value of cache-maximum-size can be absolute (such as "10G", "10M", "1K") or relative (such as "10%").

Notice how the caching options interact:

- Setting `cache-minimum-disk-space=10%` implies `cache-maximum-size=90%`.
- But setting `cache-maximum-size` does not ensure any `cache-minimum-disk-space` because the disk can be filled by data otherwise.

.. warning::

    Setting limits to the cache disk usage ensures that CliMetLab triggers its cache cleaning mechanism before downloading additional data, but it has some limitations.
    As long as the limits are not reached, CliMetLab can add more data into the cache.

    For instance, when downloading a 100G file on your empty disk of 10G total, the download is attempted (since the limits are not reached) and fills the disk and fails with a disk full.





Caching options (TODO : restrict to 'cach.*' options)
-----------------------------------------------------

.. module-output:: generate_settings_rst

    "cache-minimum-disk-space": (
        "10%"
        "Minimum space that must be left on the filesystem containing the cache directory.",
    ),
    "cache-maximum-size": (
        "80%",
        "Maximum disk space used by the CliMetLab cache.",
    ),


Internals
---------

Internally, CliMetLab cache is managed by the module `climetlab.core.cache`, it relies on a sqlite database. The :py:func:`cache_file` function provide a unique path for a given couple (`owner`, `args`). The calling code is responsible for checking if the file exists and decide to read it or create it.

"""  # noqa: E501

import datetime
import hashlib
import json
import os
import sqlite3
import tempfile
import threading

from climetlab.utils import bytes_to_string
from climetlab.utils.html import css

from .settings import SETTINGS


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
            cache_db = os.path.join(cache_dir, "cache.db")
            self.db = sqlite3.connect(cache_db)
            # So we can use rows as dictionaries
            self.db.row_factory = sqlite3.Row

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


def settings_changed():
    """Need to be called when the settings has been changed to update the connection to the cache database."""
    if connection.db is not None:
        connection.db.close()
    connection.db = None


SETTINGS.on_change(settings_changed)


def purge_cache(owner):
    with connection as db:
        db.execute("DELETE FROM cache WHERE owner=?", (owner,))
        db.commit()


def get_cached_files():
    with connection as db:
        for n in db.execute("SELECT * FROM cache").fetchall():
            n = dict(n)
            n["args"] = json.loads(n["args"])
            yield n


def update_cache(clean=False):
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

    with connection as db:

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

        update_cache(True)

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
