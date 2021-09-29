# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from termcolor import colored



class SettingsCmd:

    def do_settings(self, args):
        from climetlab import settings
        words = [x.strip() for x in args.split(" ") if x.strip()]


        if len(words) == 0:
            for f in settings.dump():
                print(colored(f[0], "blue"), f[1])
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
