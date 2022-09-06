# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import json
import logging
import os

from climetlab.readers.grib.parsing import (
    GribIndexingDirectoryParserIterator,
    _index_path,
    _index_url,
)
from climetlab.utils.humanize import plural, seconds

from .tools import parse_args

LOG = logging.getLogger(__name__)


class GribCmd:
    @parse_args(
        paths_or_urls=(
            None,
            dict(
                metavar="PATH_OR_URL",
                type=str,
                nargs="+",
                help="list of files or directories or urls to index",
            ),
        ),
        # json=dict(action="store_true", help="produce a JSON output"),
        baseurl=dict(
            metavar="BASEURL",
            type=str,
            help="Base url to use as a prefix to happen on each PATHS_OR_URLS to build urls.",
        ),
    )
    def do_index_gribs(self, args):
        """Create index files for grib files.
        If the option --baseurl is provided, create an index for multiple gribs.
        See https://climetlab.readthedocs.io/contributing/grib.html for details.
        """
        for path_or_url in args.paths_or_urls:
            if args.baseurl:
                entries = _index_url(
                    url=f"{args.baseurl}/{path_or_url}", path_name=path_or_url
                )
            elif os.path.exists(path_or_url):
                entries = _index_path(path_or_url)
            elif path_or_url.startswith("https://"):
                entries = _index_url(url=path_or_url, path_name=False)
            else:
                raise ValueError(f'Cannot find "{path_or_url}" to index it.')

            for e in entries:
                print(json.dumps(e))

    @parse_args(
        directory=(None, dict(help="Directory containing the GRIB files to index.")),
        format=dict(
            default="sql",
            metavar="FORMAT",
            type=str,
            help="sql or json or stdout.",
        ),
        force=dict(action="store_true", help="overwrite existing index."),
        ignore=dict(help="files to ignore.", nargs="*"),
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
        directory = args.directory
        db_path = args.output
        force = args.force
        ignore = args.ignore
        force_relative_paths_on = args.relative_paths
        db_format = args.format

        followlinks = True
        if args.no_follow_links:
            followlinks = False

        assert os.path.isdir(directory), directory

        from climetlab.sources.directory import DirectorySource

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

        def default_db_path():
            path = dict(
                json=os.path.join(directory, DirectorySource.DEFAULT_JSON_FILE),
                sql=os.path.join(directory, DirectorySource.DEFAULT_DB_FILE),
                stdout=None,
            )[db_format]
            return path

        if db_path is None:
            db_path = default_db_path()

        def check_overwrite(filename, force):
            if not os.path.exists(filename):
                return
            if force:
                print(f"File {filename} already exists, overwriting it.")
                os.unlink(filename)
                return
            raise Exception(
                f"ERROR: File {filename} already exists (use --force to overwrite)."
            )

        if db_path is not None:
            check_overwrite(db_path, force)

        if ignore is None:
            ignore = []
        ignore.append(DirectorySource.DEFAULT_DB_FILE)
        ignore.append(DirectorySource.DEFAULT_JSON_FILE)
        ignore.append("climetlab.index.*")
        ignore.append("*.idx")
        ignore.append("*.json")
        ignore.append("*.yaml")
        ignore.append("*.yml")
        ignore.append("*.pdf")
        ignore.append("*.txt")
        ignore.append("*.html")
        ignore.append(".*")
        if db_path is not None:
            ignore.append(db_path)

        _index_directory(
            directory,
            db_path=db_path,
            relative_paths=relative_paths,
            followlinks=followlinks,
            ignore=ignore,
            db_format=db_format,
        )

    @parse_args(
        filename=(None, dict(help="Database filename.")),
    )
    def do_dump_index(self, args):
        from climetlab.indexing.database.sql import SqlDatabase

        db = SqlDatabase(db_path=args.filename)
        for d in db.dump_dicts():
            print(json.dumps(d))


def _index_directory(
    directory,
    db_path,
    relative_paths,
    followlinks,
    ignore,
    db_format,
):
    from climetlab.indexing.database.json import JsonDatabase
    from climetlab.indexing.database.sql import SqlDatabase
    from climetlab.indexing.database.stdout import StdoutDatabase

    db = dict(json=JsonDatabase, sql=SqlDatabase, stdout=StdoutDatabase,)[
        db_format
    ](db_path)
    iterator = GribIndexingDirectoryParserIterator(
        directory,
        ignore=ignore,
        relative_paths=relative_paths,
        followlinks=followlinks,
    )
    start = datetime.datetime.now()
    count = db.load(iterator)
    end = datetime.datetime.now()
    print(f"Indexed {plural(count,'field')} in {seconds(end - start)}.")
