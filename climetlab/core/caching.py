# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

"""

Internally, CliMetLab cache is managed by the module `climetlab.core.cache`,
it relies on a sqlite database. The :py:func:`cache_file` function provide
a unique path for a given couple (`owner`, `args`).
The calling code is responsible for checking if the file exists and
decide to read it or create it.

"""

import ctypes
import datetime
import functools
import hashlib
import json
import logging
import os
import platform
import shutil
import sqlite3
import threading
import time

import pandas as pd
from filelock import FileLock

from climetlab.core.settings import SETTINGS
from climetlab.utils import humanize
from climetlab.utils.html import css

VERSION = 2
CACHE_DB = f"cache-{VERSION}.db"

LOG = logging.getLogger(__name__)


CONNECTION = None
CACHE = None


class DiskUsage:
    def __init__(self, path):

        path = os.path.realpath(path)
        self.path = path

        if platform.system() == "Windows":
            avail = ctypes.c_ulonglong()
            total = ctypes.c_ulonglong()
            free = ctypes.c_ulonglong()

            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(path),
                ctypes.pointer(avail),
                ctypes.pointer(total),
                ctypes.pointer(free),
            )
            self.avail = avail.value
            self.total = total.value
            self.free = free.value
        else:
            st = os.statvfs(path)
            self.free = st.f_bfree * st.f_frsize
            self.total = st.f_blocks * st.f_frsize
            self.avail = st.f_bavail * st.f_frsize

        self.percent = int(
            float(self.total - self.avail) / float(self.total) * 100 + 0.5
        )

    def __repr__(self):
        return (
            f"DiskUsage(total={self.total},free={self.free},"
            f"avail={self.avail},percent={self.percent},path={self.path})"
        )


def disk_usage(path):
    return DiskUsage(path)


def default_serialiser(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, (pd.Timestamp)):
        return o.isoformat()
    if isinstance(o, (pd.DatetimeIndex)):
        return [_.isoformat() for _ in o]
    return json.JSONEncoder.default(o)


def in_executor(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        global CACHE
        s = CACHE.enqueue(func, *args, **kwargs)
        return s.result()

    return wrapped


def in_executor_forget(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        global CACHE
        CACHE.enqueue(func, *args, **kwargs)
        return None

    return wrapped


class Future:
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._condition = threading.Condition()
        self._ready = False
        self._result = None

    def execute(self):
        try:
            self._result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            LOG.error(e)
            self._result = e
        with self._condition:
            self._ready = True
            self._condition.notify_all()

    def result(self):
        with self._condition:
            while not self._ready:
                self._condition.wait()
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


class Cache(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._connection = None
        self._queue = []
        self._condition = threading.Condition()

    def run(self):
        while True:
            with self._condition:
                while len(self._queue) == 0:
                    self._condition.wait()
                s = self._queue.pop(0)
                self._condition.notify_all()
            s.execute()

    @property
    def connection(self):
        if self._connection is None:
            self._connection = self.new_connection()

        return self._connection

    def new_connection(self):
        cache_dir = SETTINGS.get("cache-directory")
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        cache_db = os.path.join(cache_dir, CACHE_DB)
        LOG.debug("Cache database is %s", cache_db)
        connection = sqlite3.connect(cache_db)
        # So we can use rows as dictionaries
        connection.row_factory = sqlite3.Row

        # If you change the schema, change VERSION above
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                    path          TEXT PRIMARY KEY,
                    owner         TEXT NOT NULL,
                    args          TEXT NOT NULL,
                    creation_date TEXT NOT NULL,
                    flags         INTEGER DEFAULT 0,
                    owner_data    TEXT,
                    last_access   TEXT NOT NULL,
                    type          TEXT,
                    parent        TEXT,
                    replaced      TEXT,
                    extra         TEXT,
                    expires       INTEGER,
                    accesses      INTEGER,
                    size          INTEGER);"""
        )
        return connection

    def enqueue(self, func, *args, **kwargs):
        with self._condition:
            s = Future(func, args, kwargs)
            self._queue.append(s)
            self._condition.notify_all()
            return s

    def _file_in_cache_directory(self, path):
        cache_directory = SETTINGS.get("cache-directory")
        return path.startswith(cache_directory)

    def _cache_directory(self):
        cache_directory = SETTINGS.get("cache-directory")
        return cache_directory

    def _ensure_in_cache(self, path):
        assert self._file_in_cache_directory(path), f"File not in cache {path}"

    def _settings_changed(self):
        LOG.debug("Settings changed")
        self._connection = None  # The user may have changed the cache directory
        self._check_cache_size()

    def _latest_date(self):
        """Returns the latest date to be used when purging the cache.
        So we do not purge files being downloaded."""
        with self.connection as db:
            latest = db.execute(
                "SELECT MIN(creation_date) FROM cache WHERE size IS NULL"
            ).fetchone()[0]
            if latest is None:
                latest = db.execute(
                    "SELECT MAX(creation_date) FROM cache WHERE size IS NOT NULL"
                ).fetchone()[0]
            if latest is None:
                latest = datetime.datetime.now()
            return latest

    def _purge_cache(self, matcher=None):

        if matcher is None:
            self._housekeeping(clean=True)
            # _update_cache(clean=True)
            self._decache(self._cache_size(), purge=True)
            return

        dump = self._dump_cache_database(matcher)
        for entry in dump:
            self._delete_entry(entry)

    def _cache_entries(self):
        result = []
        with self.connection as db:
            for n in db.execute("SELECT * FROM cache").fetchall():
                n = dict(n)
                n["args"] = json.loads(n["args"])
                try:
                    n["owner_data"] = json.loads(n["owner_data"])
                except Exception:
                    pass
                if os.path.exists(n["path"]):
                    result.append(n)
        return result

    def _update_entry(self, path, owner_data=None):
        self._ensure_in_cache(path)

        if os.path.isdir(path):
            kind = "directory"
            size = 0
            for root, _, files in os.walk(path):
                for f in files:
                    size += os.path.getsize(os.path.join(root, f))
        else:
            kind = "file"
            size = os.path.getsize(path)

        with self.connection as db:
            db.execute(
                "UPDATE cache SET size=?, type=?, owner_data=? WHERE path=?",
                (
                    size,
                    kind,
                    json.dumps(owner_data, default=default_serialiser),
                    path,
                ),
            )

    def _update_cache(self, clean=False):
        """Update cache size and size of each file in the database ."""
        with self.connection as db:
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

    def _housekeeping(self, clean=False):
        top = SETTINGS.get("cache-directory")
        with self.connection as db:
            for name in os.listdir(top):
                if name == CACHE_DB:
                    continue

                full = os.path.join(top, name)
                count = db.execute(
                    "SELECT count(*) FROM cache WHERE path=?", (full,)
                ).fetchone()[0]

                if count > 0:
                    continue

                parent = None
                start = full.split(".")[0] + "%"
                for n in db.execute(
                    "SELECT path FROM cache WHERE parent IS NULL and path LIKE ?",
                    (start,),
                ).fetchall():
                    if full.startswith(n["path"]):
                        parent = n["path"]
                        break

                try:
                    s = os.stat(full)
                    if time.time() - s.st_mtime < 120:  # Two minutes
                        continue
                except OSError:
                    pass

                if parent is None:
                    LOG.warning(f"CliMetLab cache: orphan found: {full}")
                else:
                    LOG.debug(
                        f"CliMetLab cache: orphan found: {full} with parent {parent}"
                    )

                self._register_cache_file(
                    full,
                    "orphans",
                    None,
                    parent,
                )
        self._update_cache(clean=clean)

    def _delete_file(self, path):

        self._ensure_in_cache(path)

        try:
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path)
            else:
                os.unlink(path)
        except Exception as e:
            print(e)
            LOG.exception("Deleting %s", path)

    def _entry_to_dict(self, entry):
        n = dict(entry)
        for k in ("args", "owner_data"):
            if k in n and isinstance(n[k], str):
                try:
                    n[k] = json.loads(n[k])
                except Exception:
                    LOG.debug("Cannot decode JSON %s", n[k])
                    pass
        return n

    def _delete_entry(self, entry):
        if isinstance(entry, str):
            entry = dict(
                path=entry,
                size=0,
                owner=None,
                args=None,
            )
            try:
                entry["size"] = os.path.getsize(entry["path"])
            except OSError:
                pass

        if entry["size"] is None:
            entry["size"] = 0

        path, size, owner, args = (
            entry["path"],
            entry["size"],
            entry["owner"],
            entry["args"],
        )

        LOG.warning(
            "Deleting entry %s",
            json.dumps(
                self._entry_to_dict(entry), indent=4, default=default_serialiser
            ),
        )
        total = 0

        # First, delete child files, e.g. unzipped data
        with self.connection as db:
            for child in db.execute("SELECT * FROM cache WHERE parent = ?", (path,)):
                total += self._delete_entry(child)

        if not os.path.exists(path):
            LOG.warning(f"cache file lost: {path}")
            with self.connection as db:
                db.execute("DELETE FROM cache WHERE path=?", (path,))
            return total

        LOG.warning(f"CliMetLab cache: deleting {path} ({humanize.bytes(size)})")
        LOG.warning(f"CliMetLab cache: {owner} {args}")
        self._delete_file(path)

        with self.connection as db:
            db.execute("DELETE FROM cache WHERE path=?", (path,))

        return total + size

    def _decache(self, bytes, purge=False):
        # _find_orphans()
        # _update_cache(clean=True)

        if bytes <= 0:
            return 0

        LOG.warning("CliMetLab cache: trying to free %s", humanize.bytes(bytes))

        total = 0

        with self.connection as db:

            latest = datetime.datetime.now() if purge else self._latest_date()

            for stmt in (
                "SELECT * FROM cache WHERE size IS NOT NULL AND owner='orphans' AND creation_date < ?",
                "SELECT * FROM cache WHERE size IS NOT NULL AND creation_date < ? ORDER BY last_access ASC",
            ):
                for entry in db.execute(stmt, (latest,)):
                    total += self._delete_entry(entry)
                    if total >= bytes:
                        LOG.warning(
                            "CliMetLab cache: freed %s from cache",
                            humanize.bytes(bytes),
                        )
                        return total

        LOG.warning("CliMetLab cache: could not free %s", humanize.bytes(bytes))

    def _register_cache_file(self, path, owner, args, parent=None):
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

        self._ensure_in_cache(path)

        with self.connection as db:

            now = datetime.datetime.now()

            args = json.dumps(args, default=default_serialiser)

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
                                    accesses,
                                    parent)
                    VALUES(?,?,?,?,?,?,?)""",
                    (path, owner, args, now, now, 1, parent),
                )

            return dict(
                db.execute("SELECT * FROM cache WHERE path=?", (path,)).fetchone()
            )

    def _cache_size(self):
        with self.connection as db:
            size = db.execute("SELECT SUM(size) FROM cache").fetchone()[0]
            if size is None:
                size = 0
            return size

    def _decache_file(self, path):
        self._delete_entry(path)

    def _check_cache_size(self):

        # Check absolute limit
        size = self._cache_size()
        maximum = SETTINGS.get("maximum-cache-size")
        if maximum is not None and size > maximum:
            self._housekeeping()
            self._decache(size - maximum)

        # Check relative limit
        size = self._cache_size()
        usage = SETTINGS.get("maximum-cache-disk-usage")
        cache_directory = SETTINGS.get("cache-directory")
        df = disk_usage(cache_directory)
        if df.percent > usage:
            LOG.debug("Cache disk usage %s, limit %s", df.percent, usage)
            self._housekeeping()
            delta = (df.percent - usage) * df.total * 0.01
            self._decache(delta)

    def _repr_html_(self):
        """Return a html representation of the cache .

        Returns
        -------
        str
            HTML status of the cache.
        """

        html = [css("table")]
        with self.new_connection() as db:
            for n in db.execute("SELECT * FROM cache"):
                n = dict(n)
                n["missing"] = not os.path.exists(n["path"])
                n["temporary"] = os.path.exists(n["path"] + ".tmp") or os.path.exists(
                    n["path"] + ".tmp.download"
                )  # TODO: decide how to handle temporary extension
                if n["size"] is None:
                    n["size"] = 0
                html.append("<table class='climetlab'>")
                html.append("<td><td colspan='2'>%s</td></tr>" % (n["path"],))

                for k in [x for x in n.keys() if x not in ("path", "owner_data")]:
                    v = humanize.bytes(n[k]) if k == "size" else n[k]
                    html.append("<td><td>%s</td><td>%s</td></tr>" % (k, v))
                html.append("</table>")
                html.append("<br>")
        return "".join(html)

    def _dump_cache_database(self, matcher=lambda x: True):
        result = []
        with self.connection as db:
            for d in db.execute("SELECT * FROM cache"):
                n = dict(d)
                for k in ("args", "owner_data"):
                    if n[k] is not None:
                        n[k] = json.loads(n[k])
                if matcher(n):
                    result.append(n)
        return result

    def _summary_dump_cache_database(self, matcher=lambda x: True):
        result = self._dump_cache_database(matcher=matcher)
        count = len(result)
        size = 0
        for r in result:
            size += r.get("size", 0)
        return count, size


CACHE = Cache()
CACHE.start()

dump_cache_database = in_executor(CACHE._dump_cache_database)
summary_dump_cache_database = in_executor(CACHE._summary_dump_cache_database)
register_cache_file = in_executor(CACHE._register_cache_file)
update_entry = in_executor(CACHE._update_entry)
check_cache_size = in_executor_forget(CACHE._check_cache_size)
cache_size = in_executor(CACHE._cache_size)
cache_entries = in_executor(CACHE._cache_entries)
purge_cache = in_executor(CACHE._purge_cache)
housekeeping = in_executor(CACHE._housekeeping)
decache_file = in_executor(CACHE._decache_file)
file_in_cache_directory = in_executor(CACHE._file_in_cache_directory)
settings_changed = in_executor(CACHE._settings_changed)
cache_directory = in_executor(CACHE._cache_directory)


def cache_file(
    owner: str,
    create,
    args,
    hash_extra=None,
    extension: str = ".cache",
    force=None,
    replace=None,
):
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
    m.update(owner.encode("utf-8"))

    m.update(
        json.dumps(args, sort_keys=True, default=default_serialiser).encode("utf-8")
    )
    m.update(json.dumps(hash_extra, sort_keys=True).encode("utf-8"))
    m.update(json.dumps(extension, sort_keys=True).encode("utf-8"))

    if replace is not None:
        # Don't replace files that are not in the cache
        if not file_in_cache_directory(replace):
            replace = None

    path = os.path.join(
        SETTINGS.get("cache-directory"),
        "{}-{}{}".format(
            owner.lower(),
            m.hexdigest(),
            extension,
        ),
    )

    record = register_cache_file(path, owner, args)
    if os.path.exists(path):
        if callable(force):
            owner_data = record["owner_data"]
            if owner_data is not None:
                owner_data = json.loads(owner_data)
            force = force(args, path, owner_data)

        if force:
            decache_file(path)

    if not os.path.exists(path):

        lock = path + ".lock"

        with FileLock(lock):
            if not os.path.exists(
                path
            ):  # Check again, another thread/process may have created the file

                owner_data = create(path + ".tmp", args)

                os.rename(path + ".tmp", path)

                update_entry(path, owner_data)

                check_cache_size()

        try:
            os.unlink(lock)
        except OSError:
            pass

    return path


def auxiliary_cache_file(
    owner,
    path,
    index=0,
    content=None,
    extension=".cache",
):
    # Create an auxiliary cache file
    # to be used for example to cache an index
    # It is invalidated if `path` is changed
    stat = os.stat(path)

    def create(target, args):
        # Simply touch the file
        with open(target, "w") as f:
            if content:
                f.write(content)

    return cache_file(
        owner,
        create,
        (
            path,
            stat.st_ctime,
            stat.st_mtime,
            stat.st_size,
            index,
        ),
        extension=extension,
    )


# housekeeping()
SETTINGS.on_change(settings_changed)
