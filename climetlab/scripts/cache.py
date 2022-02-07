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

from termcolor import colored

from climetlab.utils import humanize
from climetlab.utils.dates import to_datetime

from .tools import parse_args, print_table

EPILOG = """
SIZE can be expressed using suffixes such a K, M, G, etc. For example
``--larger 1G`` will match all cache entries larger than 1 GiB.

DATE can be expressed as absolute time like ``2021-10-10T22:59:00``` or relative such
as ``1h`` (one hour ago) or ``2d`` (two days ago).

The ``--older`` and ``--newer`` consider the *creation date* of
cache entries, unless ``--accessed`` is specified. In this case the time of
*last access* is used.

Example, to remove large files not accessed for one week:

   ``decache --accessed --older 1w --larger 1G``

"""

MATCHER = dict(
    epilog=EPILOG,
    match=dict(type=str, metavar="STRING", help="TODO"),
    newer=dict(type=str, metavar="DATE", help="TODO"),
    older=dict(type=str, metavar="DATE", help="TODO"),
    accessed=dict(
        action="store_true",
        help="use the date of last access instead of the creation date",
    ),
    larger=dict(
        type=str,
        metavar="SIZE",
        help="consider only cache entries that are larger than SIZE bytes",
    ),
    smaller=dict(
        type=str,
        metavar="SIZE",
        help="consider only cache entries that are smaller than SIZE bytes",
    ),
)


def parse_size(txt):
    return humanize.as_bytes(txt)


def parse_user_date(value):
    try:
        return to_datetime(value)
    except ValueError:
        return datetime.datetime.now() - humanize.as_timedelta(value)


class Matcher:
    def __init__(self, args):
        self.message = []

        for k in MATCHER.keys():
            if k != "epilog":
                setattr(self, k, getattr(args, k))

        if self.match is not None:
            self.message.append(f"matching '{self.match}'")

        if self.newer is not None:
            self.newer = parse_user_date(self.newer)
            value = humanize.rounded_datetime(self.newer)
            self.message.append(f"newer than '{value}'")

        if self.older is not None:
            self.older = parse_user_date(self.older)
            value = humanize.rounded_datetime(self.older)
            self.message.append(f"older than '{value}'")

        if self.smaller is not None:
            self.smaller = parse_size(self.smaller)
            value = humanize.bytes(self.smaller)
            self.message.append(f"smaller than {value}")

        if self.larger is not None:
            self.larger = parse_size(self.larger)
            value = humanize.bytes(self.larger)
            self.message.append(f"larger than {value}")

        self.undefined = len(self.message) == 0

    def __call__(self, entry):
        if self.undefined:
            return True

        if self.smaller is not None:
            if entry["size"] is None or entry["size"] > self.smaller:
                return False

        if self.larger is not None:
            if entry["size"] is None or entry["size"] < self.larger:
                return False

        creation_date = to_datetime(entry["creation_date"])

        if self.newer is not None:
            if creation_date < self.newer:
                return False

        if self.older is not None:
            if creation_date > self.older:
                return False

        if self.match is not None:
            if not self._match(entry):
                return False

        # accesses
        # last_access

        return True

    def _match(self, entry):

        if isinstance(entry, (list, tuple)):
            return any(self._match(x) for x in entry)

        if isinstance(entry, dict):
            return any(self._match(x) for x in entry.values())

        return self.match in str(entry)


class CacheCmd:
    @parse_args(
        json=dict(action="store_true", help="produce a JSON output"),
        all=dict(action="store_true"),
        path=dict(
            action="store_true", help="print the path of cache directory and exit"
        ),
        sort=dict(
            type=str,
            metavar="KEY",
            help="sort output according to increasing values of KEY.",
        ),
        reverse=dict(
            action="store_true",
            help="reverse the order of the sort, from larger to smaller",
        ),
        **MATCHER,
    )
    def do_cache(self, args):
        """
        Cache command to inspect the CliMetLab cache.
        The selection arguments are the same as for the ``climetlab decache`` deletion
        command.
        Examples: climetlab cache --all
        """
        from climetlab.core.caching import cache_directory, dump_cache_database

        if args.path:
            print(cache_directory())
            return

        matcher = Matcher(args)
        if not args.json and not matcher.undefined:
            message = humanize.list_to_human(matcher.message)
            print(colored(f"Entries {message}.", "green"))

        cache = dump_cache_database(matcher=matcher)

        if args.sort:
            kind = None
            for e in cache:
                if e[args.sort] is not None:
                    kind = type(e[args.sort])
                    break

            if kind is not None:
                _ = {
                    dict: lambda x: tuple() if x is None else tuple(sorted(x.items())),
                    str: lambda x: "" if x is None else x,
                    int: lambda x: 0 if x is None else x,
                }[kind]

                cache = sorted(
                    cache,
                    key=lambda x: _(x[args.sort]),
                    reverse=args.reverse,
                )

        if args.json:
            print(json.dumps(cache, sort_keys=True, indent=4))
            return

        if args.all:

            for entry in cache:
                print(colored(entry.pop("path"), "blue"))
                for k in (
                    "creation_date",
                    "last_access",
                    "accesses",
                    "type",
                    "size",
                    "owner",
                ):
                    print(" ", f"{k}:", colored(entry.pop(k), "green"))
                for k in sorted(entry.keys()):
                    print(" ", f"{k}:", colored(entry.pop(k), "green"))
                print()

            return

        def generate_table():

            youngest_created = None
            oldest_created = None
            youngest_accessed = None
            oldest_accessed = None
            total = 0
            for i, entry in enumerate(cache):
                if entry["size"] is not None:
                    total += entry["size"]

                if i == 0:
                    youngest_accessed = oldest_accessed = entry["last_access"]
                    youngest_created = oldest_created = entry["creation_date"]

                youngest_accessed = max(youngest_accessed, entry["last_access"])
                oldest_accessed = min(oldest_accessed, entry["last_access"])
                youngest_created = max(youngest_created, entry["last_access"])
                oldest_created = min(oldest_created, entry["last_access"])

            yield ("Cache directory:", cache_directory())
            yield ("Cache size:", humanize.bytes(total))
            yield ("Number of entries in cache:", humanize.number(len(cache)))

            if youngest_accessed:
                yield (
                    "Most recently accessed:",
                    humanize.when(datetime.datetime.fromisoformat(youngest_accessed)),
                )
                yield (
                    "Least recently accessed:",
                    humanize.when(datetime.datetime.fromisoformat(oldest_accessed)),
                )
                yield (
                    "Youngest entry:",
                    humanize.when(datetime.datetime.fromisoformat(youngest_created)),
                )
                yield (
                    "Oldest entry:",
                    humanize.when(datetime.datetime.fromisoformat(oldest_created)),
                )

        print_table(generate_table())

    @parse_args(
        all=dict(action="store_true"),
        **MATCHER,
    )
    def do_decache(self, args):
        """
        Cache deletion command (decache) to clean the cache from selected files.
        The selection arguments are the same as for the ``climetlab cache`` query
        command.
        """

        from climetlab.core.caching import purge_cache

        matcher = Matcher(args)
        if not matcher.undefined:
            message = humanize.list_to_human(matcher.message)
            print(colored(f"Purging cache entries {message}.", "green"))
            purge_cache(matcher=matcher)
            return

        if args.all:
            purge_cache()
            return

        print(
            colored(
                "To wipe the cache completely, please use the --all flag. Use --help for more information.",
                "red",
            )
        )


CacheCmd.do_decache.__doc__ += "Hello"
