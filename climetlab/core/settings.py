# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import yaml
import sys


class Settings:
    def __init__(self, defaults):
        self._settings = dict(**defaults)

    def get(self, name):
        return self._settings[name]


default_settings = dict(cache_directory="/var/tmp")

try:
    user_climetlab = os.path.expanduser("~/.climetlab")
    if not os.path.exists(user_climetlab):
        os.mkdir(user_climetlab, 0o700)

    settings_yaml = os.path.expanduser("~/.climetlab/settings.yaml")
    if not os.path.exists(settings_yaml):
        with open(settings_yaml, "w") as f:
            yaml.dump(default_settings, f, default_flow_style=False)

except Exception as e:
    print(
        "Cannot create CliMetLab settings directory, using defaults (%s)" % (e,),
        file=sys.stderr,
    )


settings = dict(**default_settings)
try:
    with open(settings_yaml) as f:
        s = yaml.load(f, Loader=yaml.SafeLoader)
        settings.update(s)

except Exception as e:
    print("Cannot load CliMetLab settings, using defaults (%s)" % (e,), file=sys.stderr)

SETTINGS = Settings(settings)
