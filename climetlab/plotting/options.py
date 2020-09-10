# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


class Options:
    def __init__(self, options=None):
        self._options = {} if options is None else options
        self._used_options = set()

    def __getitem__(self, name: str):
        self._used_options.add(name)
        return self._options[name]

    def __call__(self, name: str, default):
        self._used_options.add(name)
        return self._options.get(name, default)

    def provided(self, name: str) -> bool:
        return name in self._options

    def check_unused(self):
        unused = set(self._options.keys()) - self._used_options
        if unused:
            raise TypeError(
                "".join(
                    [
                        "Unused argument%s: " % ("s" if len(unused) > 1 else "",),
                        ", ".join("%s=%s" % (x, self._options[x]) for x in unused),
                    ]
                )
            )

    def update_if_not_set(self, **kwargs):
        for k, v in kwargs.items():
            if k not in self._options:
                self._options[k] = v
