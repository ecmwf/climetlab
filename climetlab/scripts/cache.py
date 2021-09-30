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

from .tools import parse_args


class CacheCmd:
    @parse_args(
        json=True,
        full=dict(action="store_true"),
        path=dict(action="store_true"),
    )
    def do_cache(self, args):
        from climetlab.core.caching import cache_directory, dump_cache_database

        cache = dump_cache_database()

        if args.json:
            print(json.dumps(cache, sort_keys=True, indent=4))
            return

        if args.path:
            print(cache_directory())
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
        print("Cache directory:", cache_directory())
        print("Cache size:", humanize.bytes(total))
        print("Number of entries in cache:", humanize.number(len(cache)))
        if youngest_accessed:
            print(
                "Most recently accessed:",
                humanize.when(datetime.datetime.fromisoformat(youngest_accessed)),
            )
            print(
                "Least recently accessed:",
                humanize.when(datetime.datetime.fromisoformat(oldest_accessed)),
            )
            print(
                "Youngest entry:",
                humanize.when(datetime.datetime.fromisoformat(youngest_created)),
            )
            print(
                "Oldest entry:",
                humanize.when(datetime.datetime.fromisoformat(oldest_created)),
            )

    def do_decache(self, args):
        from climetlab.core.caching import purge_cache

        purge_cache()
