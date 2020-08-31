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
import getpass

DEFAULTS = dict(cache_directory="/var/tmp/climetlab-%s" % (getpass.getuser(),))

NONE = object()


class Settings:
    def __init__(self, settings_yaml: str, defaults: dict):
        self._settings = dict(**defaults)
        self._callbacks = []
        self._settings_yaml = settings_yaml

    def get(self, name: str, default=NONE):
        """[summary]

        Args:
            name (str): [description]
            default ([type], optional): [description]. Defaults to NONE.

        Returns:
            [type]: [description]
        """
        if default is NONE:
            return self._settings[name]
        else:
            return self._settings.get(name, default)

    def set(self, name, value):
        self._settings[name] = value
        self.changed()

    def reset(self, name: str = None):
        if name is None:
            self._settings = dict(**DEFAULTS)
        else:
            self._settings.pop(name, None)
            if name in DEFAULTS:
                self._settings[name] = DEFAULTS[name]
        self.changed()

    def _repr_html_(self):
        html = []
        html.append("<table>")
        for k, v in sorted(self._settings.items()):
            html.append("<tr><td>%s</td><td>%r</td></td>" % (k, v))
        html.append("</table>")
        return "".join(html)

    def changed(self):
        self.save()
        for cb in self._callbacks:
            cb()

    def on_change(self, callback):
        self._callbacks.append(callback)

    def save(self):
        try:
            with open(self._settings_yaml, "w") as f:
                yaml.dump(self._settings, f, default_flow_style=False)
        except Exception as e:
            print("Cannot save CliMetLab settings (%s)" % (e,), file=sys.stderr)

    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            return super().__setattr__(name, value)
        self.set(name, value)
        return value

    def __delattr__(self, name):
        if name.startswith("_"):
            return super().__delattr__(name)
        self.reset(name)


try:
    user_climetlab = os.path.expanduser("~/.climetlab")
    if not os.path.exists(user_climetlab):
        os.mkdir(user_climetlab, 0o700)

    settings_yaml = os.path.expanduser("~/.climetlab/settings.yaml")
    if not os.path.exists(settings_yaml):
        with open(settings_yaml, "w") as f:
            yaml.dump(DEFAULTS, f, default_flow_style=False)

except Exception as e:
    print(
        "Cannot create CliMetLab settings directory, using defaults (%s)" % (e,),
        file=sys.stderr,
    )


settings = dict(**DEFAULTS)
try:
    with open(settings_yaml) as f:
        s = yaml.load(f, Loader=yaml.SafeLoader)
        settings.update(s)

except Exception as e:
    print("Cannot load CliMetLab settings, using defaults (%s)" % (e,), file=sys.stderr)

SETTINGS = Settings(settings_yaml, settings)
