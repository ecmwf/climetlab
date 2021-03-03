# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import getpass
import logging
import os
import tempfile
from typing import Callable

import yaml

from climetlab.utils.html import css

LOG = logging.getLogger(__name__)

DOT_CLIMETLAB = os.path.expanduser("~/.climetlab")

SETTINGS_AND_HELP = {
    "cache-directory": (
        os.path.join(tempfile.gettempdir(), "climetlab-%s" % (getpass.getuser(),)),
        """Directory of where the dowloaded files are cached, with ``${USER}`` is the user id.
        See :ref:`caching` for more information.""",
    ),
    "styles-directories": (
        [os.path.join(DOT_CLIMETLAB, "styles")],
        """List of directories where to search for styles definitions.
        See :ref:`styles` for more information.""",
    ),
    "projections-directories": (
        [os.path.join(DOT_CLIMETLAB, "projections")],
        """List of directories where to search for projections definitions.
        See :ref:`projections` for more information.""",
    ),
    "layers-directories": (
        [os.path.join(DOT_CLIMETLAB, "layers")],
        """List of directories where to search for layers definitions.
        See :ref:`layers` for more information.""",
    ),
    "plotting-options": (
        {},
        """Dictionary of default plotting options.
           See :ref:`plotting` for more information.""",
    ),
}

DEFAULTS = {}
for k, v in SETTINGS_AND_HELP.items():
    DEFAULTS[k] = v[0]


NONE = object()


class Settings:
    def __init__(self, settings_yaml: str, defaults: dict):
        self._defaults = defaults
        self._settings = dict(**defaults)
        self._callbacks = []
        self._settings_yaml = settings_yaml
        self._pytest = None

    def get(self, name: str, default=NONE):
        """[summary]

        Args:
            name (str): [description]
            default ([type], optional): [description]. Defaults to NONE.

        Returns:
            [type]: [description]
        """

        if name not in DEFAULTS:
            raise KeyError("No setting name '%s'" % (name,))

        if default is NONE:
            return self._settings[name]

        return self._settings.get(name, default)

    def set(self, name: str, *args, **kwargs):
        """[summary]

        Args:
            name (set): [description]
            value ([type]): [description]
        """

        if name not in DEFAULTS:
            raise KeyError("No setting name '%s'" % (name,))

        klass = type(DEFAULTS[name])

        if klass in (bool, int, float, str):
            # TODO: Proper exceptions
            assert len(args) == 1
            assert len(kwargs) == 0
            value = args[0]

        if klass is list:
            assert len(args) > 0
            assert len(kwargs) == 0
            value = list(args)
            if len(args) == 1 and isinstance(args[0], list):
                value = args[0]

        if klass is dict:
            assert len(args) <= 1
            if len(args) == 0:
                assert len(kwargs) > 0
                value = kwargs

            if len(args) == 1:
                assert len(kwargs) == 0
                value = args[0]

        if not isinstance(value, klass):
            raise TypeError("Setting '%s' must be of type '%s'" % (name, klass))

        self._settings[name] = value
        self._changed()

    def reset(self, name: str = None):
        """Reset setting(s) to default values.

        Args:
            name (str, optional): The name of the setting to reset to default. If the setting does not have a default,
            it is removed. If `None` is passed, all settings are reset to their default values. Defaults to None.
        """
        if name is None:
            self._settings = dict(**DEFAULTS)
        else:
            if name not in DEFAULTS:
                raise KeyError("No setting name '%s'" % (name,))

            self._settings.pop(name, None)
            if name in DEFAULTS:
                self._settings[name] = DEFAULTS[name]
        self._changed()

    def _repr_html_(self):
        html = [css("table")]
        html.append("<table class='climetlab'>")
        for k, v in sorted(self._settings.items()):
            html.append(
                "<tr><td>%s</td><td>%r</td><td>%r</td></td>"
                % (k, v, SETTINGS_AND_HELP.get(k, (None, "..."))[0])
            )
        html.append("</table>")
        return "".join(html)

    def _changed(self):
        self._save()
        for cb in self._callbacks:
            cb()

    def on_change(self, callback: Callable[[], None]):
        self._callbacks.append(callback)

    def _save(self):

        try:
            with open(self._settings_yaml, "w") as f:
                yaml.dump(self._settings, f, default_flow_style=False)
        except Exception:
            LOG.error(
                "Cannot save CliMetLab settings (%s)",
                self._settings_yaml,
                exc_info=True,
            )


try:
    if not os.path.exists(DOT_CLIMETLAB):
        os.mkdir(DOT_CLIMETLAB, 0o700)

    settings_yaml = os.path.expanduser("~/.climetlab/settings.yaml")
    if not os.path.exists(settings_yaml):
        with open(settings_yaml, "w") as f:
            yaml.dump(DEFAULTS, f, default_flow_style=False)

except Exception:
    LOG.error(
        "Cannot create CliMetLab settings directory, using defaults (%s)",
        settings_yaml,
        exc_info=True,
    )


settings = dict(**DEFAULTS)
try:
    with open(settings_yaml) as f:
        s = yaml.load(f, Loader=yaml.SafeLoader)
        settings.update(s)

except Exception:
    LOG.error(
        "Cannot load CliMetLab settings (%s), reverting to defaults",
        settings_yaml,
        exc_info=True,
    )

SETTINGS = Settings(settings_yaml, settings)
