# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import json

from .tools import parse_args, print_table


class SettingsCmd:
    @parse_args(
        json=dict(action="store_true", help="produce a JSON output"),
        args=dict(metavar="ARG", type=str, nargs="*"),
    )
    def do_settings(self, args):
        from climetlab import settings

        words = args.args

        if len(words) == 0:
            if args.json:
                result = {}
                for f in settings.dump():
                    result[f[0]] = f[1]
                print(json.dumps(result, indent=4, sort_keys=True))
                return

            print_table((f[0], f[1]) for f in settings.dump())
            return

        if len(words) == 1:
            name = words[0]
            print(settings.get(name))
            return

        if len(words) == 2:
            name = words[0]
            value = words[1]
            settings.set(name, value)

    def complete_settings(self, text, line, start_index, end_index):
        from climetlab import settings

        names = [f[0] for f in settings.dump()]
        return [t for t in names if t.startswith(text)]
