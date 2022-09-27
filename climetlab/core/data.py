# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import inspect
import logging
import os
from collections import defaultdict

import yaml

from climetlab.core.plugins import directories
from climetlab.decorators import locked
from climetlab.utils.html import css
from climetlab.utils.kwargs import merge_dicts

LOG = logging.getLogger(__name__)


YAML_FILES = None

IGNORE = [
    "magics.yaml",
    "colours.yaml",
    "conventions.yaml",
    "config.yaml",
    "units.yaml",
]


def _guess(data, path):
    if "areas" in data:
        return "domains"

    if "dataset" in data:
        return "datasets"

    if "magics" in data:

        if "msymb" in data["magics"]:
            return "styles"

        if "mcont" in data["magics"]:
            return "styles"

        if "mcoast" in data["magics"]:
            return "layers"

        if "mmap" in data["magics"]:
            return "projections"

        LOG.warning("Cannot guess collection for %s", path)

    if "dask" in data:
        return "dask"

    return "unknown"


class Entry:
    def __init__(self, name, kind, root, path, data, owner):
        self.name = name
        self.root = root
        self.kind = kind
        self.path = path
        self.data = data
        self.hidden = data.get("hidden", False)
        self.owner = owner
        self.next = None

    def _repr_html_(self):
        html = [
            css("table"),
            "<table class='climetlab'>",
            "<tr><td>Name:</td><td>%s</td></tr>" % self.name,
            "<tr><td>Collection:</td><td>%s</td></tr>" % self.kind,
            "<tr><td>Path:</td><td>%s</td></tr>" % self.path,
        ]

        html.append(
            "<tr><td>Definition:</td><td><pre>%s</pre></td></tr>"
            % (yaml.dump(self.data, default_flow_style=False),)
        )
        html.append("</table>")
        return "".join(html)

    def __repr__(self):
        return f"Entry({self.name}, path={self.path})"

    def choices(self):
        result = {self.owner: self}
        if self.next:
            result.update(self.next.choices())
        return result


@locked
def _load_yaml_files():
    global YAML_FILES
    if YAML_FILES is not None:
        return YAML_FILES

    YAML_FILES = defaultdict(dict)
    for owner, directory in directories(owner=True):
        for root, _, files in os.walk(directory):
            for file in [f for f in files if f.endswith(".yaml")]:
                if file in IGNORE:
                    continue
                path = os.path.join(root, file)
                try:
                    with open(path) as f:
                        data = yaml.load(f.read(), Loader=yaml.SafeLoader)
                        if not isinstance(data, dict):
                            continue
                        name, _ = os.path.splitext(os.path.basename(path))
                        kind = _guess(data, path)
                        collection = YAML_FILES[kind]
                        e = Entry(name, kind, directory, path, data, owner)
                        if name in collection:
                            e.next = collection[name]
                        collection[name] = e

                except Exception:
                    LOG.exception("Cannot process YAML file %s (%s)", path, owner)

    return YAML_FILES


def get_data_entry(kind, name, default=None, merge=False):
    """Read various config files to get the config values of
    a given kind.

    kind: Can be "layers", "projections", "dask", etc..
    name: The filename of the config file to read is something like {name}.yaml
    default: is a default dict when no config file is found
    merge: if False, only one config file will be used.
           if True, config files will be merged according to a given priority order.

    When looking for config files from a climetlab plugin, the config file provided
    by the plugin (if it exists) will be given higher priority than the file provided by
    climetlab.
    User-defined settings are always higher priority.
    """

    PRIORITIES = {
        # HIGHEST PRIORITY
        # "environment-variable": 6,
        "user-settings": 5,
        # "system-settings": 4,
        "plugins": 3,
        "climetlab": 2,
        "default": 1,
        # LOWEST PRIORITY
    }

    # TODO: default is not used. Remove it?
    # TODO: merge is not used.Remove it?

    files = _load_yaml_files()

    if kind not in files:
        if default is not None:
            return default
        raise KeyError("No collection named '%s'" % (kind,))

    if name not in files[kind]:
        if default is not None:
            return default
        raise KeyError(
            "No object '%s' in collection named '%s' (%s)"
            % (name, kind, sorted(files[kind].keys()))
        )

    choices = files[kind][name].choices()
    assert len(choices) != 0

    if len(choices) == 1:
        return list(choices.values())[0]

    frame = inspect.currentframe()
    caller = inspect.getouterframes(frame, 0)

    def is_active(owner, entry):
        # always active
        if owner in PRIORITIES:
            return True
        # check if called from the code inside a plugin
        for c in caller:
            if c.filename.startswith(entry.root):
                return True
        return False

    if default is not None:
        choices["default"] = Entry(
            name="default",
            kind="default",
            root=None,
            path=None,
            data=default,
            owner="default",
        )

    choices = {k: v for k, v in choices.items() if is_active(k, v)}
    selected = [
        v
        for _, v in sorted(
            choices.items(), key=lambda x: PRIORITIES.get(x[0], PRIORITIES["plugins"])
        )
    ]

    if not merge:
        return selected[0]

    data = merge_dicts(*[v.data for v in selected])
    return Entry(
        name="merged",
        kind=kind,
        root=None,
        path=None,
        data=data,
        owner="merged",
    )


def data_entries(kind=None):
    if kind is None:
        for collection in _load_yaml_files().items():
            for entry in collection.values():
                if not entry.hidden:
                    yield entry
    else:
        for entry in _load_yaml_files().get(kind, {}).values():
            if not entry.hidden:
                yield entry


@locked
def clear_cache():
    global YAML_FILES
    YAML_FILES = None
