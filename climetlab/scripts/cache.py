# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json

# from termcolor import colored


class CacheCmd:
    def do_cache(self, args):
        from climetlab.core.caching import dump_cache_database

        for i in dump_cache_database():
            print(json.dumps(i, sort_keys=True, indent=4))

    def do_decache(self, args):
        from climetlab.core.caching import purge_cache

        purge_cache()
