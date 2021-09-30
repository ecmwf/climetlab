# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json

from termcolor import colored

from .parse import parse_args


class CacheCmd:
    @parse_args(json=True)
    def do_cache(self, args):
        from climetlab.core.caching import dump_cache_database

        if args.json:
            print(json.dumps(dump_cache_database(), sort_keys=True, indent=4))
            return

        for entry in dump_cache_database():
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
            print()

    def do_decache(self, args):
        from climetlab.core.caching import purge_cache

        purge_cache()
