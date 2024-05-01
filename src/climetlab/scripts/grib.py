# (C) Copyright 2021 ECMWF.
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
import sys

from climetlab.indexing.database.json import JsonStdoutDatabase
from climetlab.readers.grib.parsing import (
    GribIndexingDirectoryParserIterator,
    _index_url,
)

from .tools import parse_args

LOG = logging.getLogger(__name__)


class GribCmd:
    @parse_args(
        urls=(
            None,
            dict(metavar="URLS", type=str, nargs="+", help="List of urls to index."),
        ),
        baseurl=dict(
            metavar="BASEURL",
            type=str,
            help="Base url to use as a prefix to happen on each URLS to build actual urls.",
        ),
    )
    def do_index_urls(self, args):
        """Create json index files for remote Grib urls.
        If the option --baseurl is provided, the given url are relative to the BASEURL.
        This allows creating an index for multiple gribs."""

        if args.baseurl:

            def resolve_url(u):
                if u.startswith(args.baseurl):
                    # already absolute url
                    return u
                return f"{args.baseurl}/{u}"

        else:

            def resolve_url(url):
                return url

        stdout = JsonStdoutDatabase()
        for u in args.urls:
            url = resolve_url(u)
            for e in _index_url(url):
                e["_path"] = u
                stdout.load_iterator([e])

    @parse_args(
        url=(None, dict(metavar="URL", type=str, help="url to index")),
        # output=dict(type=str, help="Output filename"),
    )
    def do_index_url(self, args):
        """Create json index files for remote Grib url."""
        stdout = JsonStdoutDatabase()
        for e in _index_url(args.url):
            assert "_path" not in e
            stdout.load_iterator([e])

    @parse_args(
        directory=(None, dict(help="Directory containing the GRIB files to index.")),
        # pattern=dict(help="Files to index (patterns).", nargs="*"),
        no_follow_links=dict(action="store_true", help="Do not follow symlinks."),
        relative_paths=dict(
            action="store_true",
            help=(
                "Use relative paths. Default is to use relative paths, "
                "except when a custom location is provided for the index location. "
                "(when the argument --output is used, default for --relative-path is False)"
            ),
        ),
        output=(
            "--output",
            dict(
                help="Custom location of the database file, will write absolute filenames in the database."
            ),
        ),
    )
    def do_index_directory(self, args):
        """Index a directory containing GRIB files."""

        if sys.platform == "win32":
            print("Not supported on windows")
            return

        directory = args.directory
        db_path = args.output
        force_relative_paths_on = args.relative_paths

        followlinks = True
        if args.no_follow_links:
            followlinks = False

        assert os.path.isdir(directory), directory

        from climetlab.sources.indexed_directory import IndexedDirectorySource

        if force_relative_paths_on:
            relative_paths = True
        else:
            if db_path is None:
                relative_paths = True
            else:
                LOG.warning(
                    (
                        "Non-default location for the index file (--output),"
                        " using absolute path in the index (i.e. setting option --relative-paths to False)."
                    )
                )
                relative_paths = False

        if db_path is None:
            db_path = os.path.join(directory, IndexedDirectorySource.DEFAULT_DB_FILE)

        parser = GribIndexingDirectoryParserIterator(
            directory,
            db_path=db_path,
            relative_paths=relative_paths,
            followlinks=followlinks,
            with_statistics=True,
        )
        parser.load_database()

    @parse_args(filename=(None, dict(help="Database filename.")))
    def do_dump_index(self, args):
        db_path = args.filename

        from climetlab.indexing.database.sql import SqlDatabase
        from climetlab.sources.indexed_directory import IndexedDirectorySource

        if os.path.isdir(db_path):
            db_path = os.path.join(db_path, IndexedDirectorySource.DEFAULT_DB_FILE)

        db = SqlDatabase(db_path=db_path)
        for d in db.lookup_dicts():
            print(json.dumps(d))
