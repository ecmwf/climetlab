# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import logging
import os
from urllib.parse import urljoin

import requests
from multiurl import robust

from climetlab.core.caching import cache_file
from climetlab.readers.grib.index import FieldSetInFiles
from climetlab.utils import progress_bar

LOG = logging.getLogger(__name__)


class FieldsetInFilesWithDBIndex(FieldSetInFiles):
    def __init__(self, db, **kwargs):
        """Should not be instanciated directly.
        The public API are the constructors "_from*()" class methods.
        """

        self.db = db

        # self._cache is a tuple : (first, length, result). It holds one chunk of the db.
        # The third element (result) is a list of size length.
        self._cache = None
        self._dict_cache = None

        super().__init__(**kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}({self.db})"

    @property
    def availability_path(self):
        dirpath = os.path.dirname(self.db.db_path)
        return os.path.join(dirpath, "availability.pickle")

    @classmethod
    def from_iterator(
        cls,
        iterator,
        cache_metadata,
        selection=None,
        order_by=None,
        **kwargs,
    ):
        def load(target, *args):
            LOG.debug(f"Building db in {target}")
            db = cls.DBCLASS(target)
            db.load_iterator(iterator)

        db_name = cache_file(
            "grib-index",
            load,
            cache_metadata,
            hash_extra=cls.DBCLASS.VERSION,
            extension=cls.DBCLASS.EXTENSION,
        )

        db = cls.DBCLASS(db_name)

        new = cls(db=db, **kwargs)
        new = new.sel(selection)
        new = new.order_by(order_by)
        return new

    @classmethod
    def from_url(cls, url, patch_entry=None, **kwargs):
        """Create a database from a given url"""

        # If this is a file, open it without download
        if os.path.exists(url):
            return cls.from_file(path=url, **kwargs)
        if url.startswith("file://") and os.path.exists(url[7:]):
            return cls.from_file(path=url[7:], **kwargs)

        # Request to download the data
        r = robust(requests.get)(url, stream=True)
        r.raise_for_status()
        try:
            size = int(r.headers.get("Content-Length"))
        except Exception:
            size = None

        if patch_entry is None:

            def absolute_url(entry):  # closure on "url"
                entry["_path"] = urljoin(url, entry.pop("_path"))
                return entry

            patch_entry = absolute_url

        def progress(iterable):
            pbar = progress_bar(iterable=iterable, desc="Downloading index", total=size)
            for line in pbar:
                yield line
                pbar.update(len(line) + 1)

        def parse_lines(lines):
            for line in lines:
                entry = json.loads(line)
                entry = patch_entry(entry)
                yield entry

        iterator = r.iter_lines()
        iterator = progress(iterator)
        iterator = parse_lines(iterator)

        return cls.from_iterator(
            iterator=iterator,
            cache_metadata={"url": url},
            **kwargs,
        )

    @classmethod
    def from_file(cls, path, **kwargs):
        directory = os.path.dirname(path)
        size = os.path.getsize(path)

        def progress(lines):
            pbar = progress_bar(iterable=lines, desc="Parsing index", total=size)
            for line in pbar:
                yield line
                pbar.update(len(line) + 1)

        def parse_lines(lines):
            for line in lines:
                entry = json.loads(line)
                if not os.path.isabs(entry["_path"]):
                    entry["_path"] = os.path.join(directory, entry["_path"])
                yield entry

        iterator = open(path)
        iterator = progress(iterator)
        iterator = parse_lines(iterator)

        return cls.from_iterator(
            iterator=iterator,
            cache_metadata={"path": path},
            **kwargs,
        )

    @classmethod
    def from_existing_db(cls, db_path, **kwargs):
        assert os.path.exists(db_path)
        return cls(cls.DBCLASS(db_path), **kwargs)
