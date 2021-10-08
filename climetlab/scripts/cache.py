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
from climetlab.utils.dates import parse_date

from .tools import parse_args, print_table

MATCHER = dict(
    match=dict(type=str, metavar="STRING"),
    newer=dict(type=str, metavar="DATE"),
    older=dict(type=str, metavar="DATE"),
    larger=dict(type=str, metavar="SIZE"),
    smaller=dict(type=str, metavar="SIZE"),
)


def parse_size(txt):
    return int(txt)


class Matcher:
    def __init__(self, args):
        self.undefined = all(getattr(args, k) is None for k in MATCHER.keys())
        # self.undefined = [x for x in MATCHER.keys() if x not in args.keys()]

        for k in MATCHER.keys():
            setattr(self, k, getattr(args, k))
            # self[k] = args.pop(k)

        if self.newer:
            self.newer = parse_date(self.newer)

        if self.older:
            self.older = parse_date(self.older)

        if self.smaller:
            self.smaller = parse_size(self.smaller)

        if self.larger:
            self.larger = parse_size(self.larger)

    def __call__(self, entry):
        if self.undefined:
            return True

        if self.smaller is not None:
            if entry["size"] is not None:
                if entry["size"] > self.smaller:
                    return False

        if self.larger is not None:
            if entry["size"] is not None:
                if entry["size"] < self.larger:
                    return False

        creation_date = parse_date(entry["creation_date"])

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
        json=dict(action="store_true"),
        full=dict(action="store_true"),
        path=dict(action="store_true"),
        sort=dict(type=str, metavar="KEY"),
        reverse=dict(action="store_true"),
        **MATCHER,
    )
    def do_cache(self, args):
        from climetlab.core.caching import cache_directory, dump_cache_database

        if args.path:
            print(cache_directory())
            return

        cache = dump_cache_database(matcher=Matcher(args))

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

        if args.full:

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
        from climetlab.core.caching import purge_cache

        matcher = Matcher(args)
        if not matcher.undefined:
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
