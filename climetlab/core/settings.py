# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import functools
import getpass
import logging
import os
import tempfile
from contextlib import contextmanager
from typing import Callable

import yaml

from climetlab.utils.html import css
from climetlab.utils.humanize import as_bytes, as_percent, as_seconds
from climetlab.version import __version__ as VERSION

LOG = logging.getLogger(__name__)

DOT_CLIMETLAB = os.path.expanduser("~/.climetlab")


class Setting:
    def __init__(self, default, description, getter=None, none_ok=False, kind=None):
        self.default = default
        self.description = description
        self.getter = getter
        self.none_ok = none_ok
        self.kind = kind if kind is not None else type(default)

    def kind(self):
        return type(self.default)

    def save(self, name, value, f):

        for n in self.description.split("\n"):
            print(f"# {n.strip()}", file=f)
        print(file=f)
        comment = yaml.dump({name: self.default}, default_flow_style=False)
        for n in comment.split("\n"):
            if n:
                print(f"# {n}", file=f)
        if value != self.default:
            print(file=f)
            yaml.dump({name: value}, f, default_flow_style=False)


_ = Setting


SETTINGS_AND_HELP = {
    "cache-directory": _(
        os.path.join(tempfile.gettempdir(), "climetlab-%s" % (getpass.getuser(),)),
        """Directory of where the dowloaded files are cached, with ``${USER}`` is the user id.
        See :doc:`/guide/caching` for more information.""",
    ),
    "styles-directories": _(
        [os.path.join(DOT_CLIMETLAB, "styles")],
        """List of directories where to search for styles definitions.
        See :ref:`styles` for more information.""",
    ),
    "projections-directories": _(
        [os.path.join(DOT_CLIMETLAB, "projections")],
        """List of directories where to search for projections definitions.
        See :ref:`projections` for more information.""",
    ),
    "layers-directories": _(
        [os.path.join(DOT_CLIMETLAB, "layers")],
        """List of directories where to search for layers definitions.
        See :ref:`layers` for more information.""",
    ),
    "dask-directories": _(
        [os.path.join(DOT_CLIMETLAB, "dask")],
        """List of directories where to search for dask cluster definitions.
        See :ref:`dask` for more information.""",
    ),
    "datasets-directories": _(
        [os.path.join(DOT_CLIMETLAB, "datasets")],
        """List of directories where to search for datasets definitions.
        See :ref:`datasets` for more information.""",
    ),
    "datasets-catalogs-urls": _(
        ["https://github.com/ecmwf-lab/climetlab-datasets/raw/main/datasets"],
        """List of url where to search for catalogues of datasets definitions.
        See :ref:`datasets` for more information.""",
    ),
    "plotting-options": _(
        {},
        """Dictionary of default plotting options.
        See :ref:`plotting` for more information.""",
    ),
    "map-plotting-backend": _(
        "magics",
        """Default backend for plotting maps.""",
    ),
    "graph-plotting-backend": _(
        "matplotlib",
        """Default backend for plotting graphs.""",
    ),
    "number-of-download-threads": _(
        5,
        """Number of threads used to download data.""",
    ),
    "maximum-cache-size": _(
        None,
        """Maximum disk space used by the CliMetLab cache (ex: 100G or 2T).""",
        getter="_as_bytes",
        none_ok=True,
    ),
    "maximum-cache-disk-usage": _(
        "90%",
        """Disk usage threshold after which CliMetLab expires older cached entries (% of the full disk capacity).
        See :doc:`/guide/caching` for more information.""",
        getter="_as_percent",
    ),
    "url-download-timeout": _(
        "30s",
        """Timeout when downloading from an url.""",
        getter="_as_seconds",
    ),
    "check-out-of-date-urls": _(
        True,
        "Perform a HTTP request to check if the remote version of a cache file has changed",
    ),
    "download-out-of-date-urls": _(
        False,
        "Re-download URLs when the remote version of a cached file as been changed",
    ),
    "use-standalone-mars-client-when-available": _(
        True,
        "Use the standalone mars client when available instead of using the web API.",
    ),
}


NONE = object()
DEFAULTS = {}
for k, v in SETTINGS_AND_HELP.items():
    DEFAULTS[k] = v.default


@contextmanager
def new_settings(s):
    SETTINGS._stack.append(s)
    try:
        yield None
    finally:
        SETTINGS._stack.pop()
        SETTINGS._notify()


def forward(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        if self._stack:
            return func(self._stack[-1], *args, **kwargs)
        return func(self, *args, **kwargs)

    return wrapped


def save_settings(path, settings):
    LOG.debug("Saving settings")
    with open(path, "w") as f:
        print("# This file is automatically generated", file=f)
        print(file=f)

        for k, v in sorted(settings.items()):
            h = SETTINGS_AND_HELP.get(k)
            if h:
                print(file=f)
                print("#", "-" * 76, file=f)
                h.save(k, v, f)

        print(file=f)
        print("#", "-" * 76, file=f)
        print("# Version of CliMetLab", file=f)
        print(file=f)
        yaml.dump({"version": VERSION}, f, default_flow_style=False)
        print(file=f)


class Settings:
    def __init__(self, settings_yaml: str, defaults: dict, callbacks=[]):
        self._defaults = defaults
        self._settings = dict(**defaults)
        self._callbacks = [c for c in callbacks]
        self._settings_yaml = settings_yaml
        self._pytest = None
        self._stack = []

    @forward
    def get(self, name: str, default=NONE):
        """[summary]

        Args:
            name (str): [description]
            default ([type], optional): [description]. Defaults to NONE.

        Returns:
            [type]: [description]
        """

        if name not in SETTINGS_AND_HELP:
            raise KeyError("No setting name '%s'" % (name,))

        getter, none_ok = (
            SETTINGS_AND_HELP[name].getter,
            SETTINGS_AND_HELP[name].none_ok,
        )
        if getter is None:
            getter = lambda name, value, none_ok: value  # noqa: E731
        else:
            getter = getattr(self, getter)

        if default is NONE:
            return getter(name, self._settings[name], none_ok)

        return getter(name, self._settings.get(name, default), none_ok)

    @forward
    def set(self, name: str, *args, **kwargs):
        """[summary]

        Args:
            name (set): [description]
            value ([type]): [description]
        """

        if name not in SETTINGS_AND_HELP:
            raise KeyError("No setting name '%s'" % (name,))

        klass = SETTINGS_AND_HELP[name].kind

        if klass in (bool, int, float, str):
            # TODO: Proper exceptions
            assert len(args) == 1
            assert len(kwargs) == 0
            value = args[0]
            value = klass(value)

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

        getter, none_ok = (
            SETTINGS_AND_HELP[name].getter,
            SETTINGS_AND_HELP[name].none_ok,
        )
        if getter is not None:
            assert len(args) == 1
            assert len(kwargs) == 0
            value = args[0]
            # Check if value is properly formatted for getter
            getattr(self, getter)(name, value, none_ok)
        else:
            if not isinstance(value, klass):
                raise TypeError("Setting '%s' must be of type '%s'" % (name, klass))

        self._settings[name] = value
        self._changed()

    @forward
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

    @forward
    def _repr_html_(self):
        html = [css("table")]
        html.append("<table class='climetlab'>")
        for k, v in sorted(self._settings.items()):
            setting = SETTINGS_AND_HELP.get(k, None)
            default = setting.default if setting else ""
            html.append("<tr><td>%s</td><td>%r</td><td>%r</td></td>" % (k, v, default))
        html.append("</table>")
        return "".join(html)

    @forward
    def dump(self):
        for k, v in sorted(self._settings.items()):
            yield ((k, v, SETTINGS_AND_HELP.get(k)))

    def _changed(self):
        self._save()
        self._notify()

    def _notify(self):
        for cb in self._callbacks:
            cb()

    def on_change(self, callback: Callable[[], None]):
        self._callbacks.append(callback)

    def _save(self):

        if self._settings_yaml is None:
            return

        try:
            save_settings(self._settings_yaml, self._settings)
        except Exception:
            LOG.error(
                "Cannot save CliMetLab settings (%s)",
                self._settings_yaml,
                exc_info=True,
            )

    def _as_bytes(self, name, value, none_ok):
        return as_bytes(value, name=name, none_ok=none_ok)

    def _as_percent(self, name, value, none_ok):
        return as_percent(value, name=name, none_ok=none_ok)

    def _as_seconds(self, name, value, none_ok):
        return as_seconds(value, name=name, none_ok=none_ok)

    # def _as_number(self, name, value, units, none_ok):
    #     return as_number(name, value, units, none_ok)

    @forward
    def temporary(self, name=None, *args, **kwargs):
        tmp = Settings(None, self._settings, self._callbacks)
        if name is not None:
            tmp.set(name, *args, **kwargs)
        return new_settings(tmp)


save = False
settings_yaml = os.path.expanduser("~/.climetlab/settings.yaml")

try:
    if not os.path.exists(DOT_CLIMETLAB):
        os.mkdir(DOT_CLIMETLAB, 0o700)
    if not os.path.exists(settings_yaml):
        save_settings(settings_yaml, DEFAULTS)
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
        if not isinstance(s, dict):
            s = {}

        settings.update(s)

    # if s != settings:
    #     save = True

    if settings.get("version") != VERSION:
        save = True

except Exception:
    LOG.error(
        "Cannot load CliMetLab settings (%s), reverting to defaults",
        settings_yaml,
        exc_info=True,
    )

SETTINGS = Settings(settings_yaml, settings)
if save:
    SETTINGS._save()
