# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
from collections import defaultdict

import yaml

from climetlab.core.plugins import directories
from climetlab.decorators import locked
from climetlab.utils.html import css

LOG = logging.getLogger(__name__)


YAML_FILES = None

IGNORE = ["magics.yaml", "colours.yaml", "conventions.yaml"]


def _guess(data, path):
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
    return "unknown"


class Entry:
    def __init__(self, name, kind, path, data):
        self.name = name
        self.kind = kind
        self.path = path
        self.data = data
        self.hidden = data.get("hidden", False)

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


@locked
def _load_yaml_files():
    global YAML_FILES
    if YAML_FILES is not None:
        return YAML_FILES

    YAML_FILES = defaultdict(dict)
    for directory in directories():
        for root, _, files in os.walk(directory):
            for file in [f for f in files if f.endswith(".yaml")]:
                if file in IGNORE:
                    continue
                path = os.path.join(root, file)
                try:
                    with open(path) as f:
                        data = yaml.load(f.read(), Loader=yaml.SafeLoader)
                        name, _ = os.path.splitext(os.path.basename(path))
                        kind = _guess(data, path)
                        collection = YAML_FILES[kind]
                        if name in collection and path != collection[name].path:
                            LOG.warning(
                                "Duplicate entry for %s %s (using %s, ignoring %s)",
                                kind,
                                name,
                                collection[name].path,
                                path,
                            )
                        else:
                            collection[name] = Entry(name, kind, path, data)

                except Exception:
                    LOG.error("Cannot process YAML file %s", path, exc_info=True)
                    raise

    return YAML_FILES


def get_data_entry(kind, name):
    files = _load_yaml_files()

    if kind not in files:
        raise KeyError("No collection named '%s'" % (kind,))

    if name not in files[kind]:
        raise KeyError(
            "No object '%s' in collection named '%s'"
            % (
                name,
                kind,
            )
        )

    return files[kind][name]


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
