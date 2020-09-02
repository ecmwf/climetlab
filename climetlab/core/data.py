# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.core.plugins import directories
import os
import yaml
from collections import defaultdict
import logging
from climetlab.utils.html import css

LOG = logging.getLogger(__name__)


YAML_FILES = None


def _guess(data):
    if "dataset" in data:
        return "datasets"

    if "magics" in data:

        if "msymb" in data["magics"]:
            return "styles"

        if "mcount" in data["magics"]:
            return "styles"

        if "mcoast" in data["magics"]:
            return "layers"

        if "mmap" in data["magics"]:
            return "projections"

    return "unknown"


class Entry:
    def __init__(self, name, kind, path, data):
        self.name = name
        self.kind = kind
        self.path = path
        self.data = data
        self.hidden = data.get("hidden", False)

    def _repr_html_(self):
        html = [css("table")]
        html.append("<table class='climetlab'>")
        html.append("<tr><td>Name:</td><td>%s</td></tr>" % self.name)
        html.append("<tr><td>Collection:</td><td>%s</td></tr>" % self.kind)
        html.append("<tr><td>Path:</td><td>%s</td></tr>" % self.path)
        html.append("<tr><td>Definition:</td><td><pre>%s</pre></td></tr>" % (yaml.dump(self.data, default_flow_style=False),))
        html.append("</table>")
        return "".join(html)



def _load_yaml_files():
    global YAML_FILES
    if YAML_FILES is not None:
        return YAML_FILES

    YAML_FILES = defaultdict(dict)
    for root, _, files in os.walk(*directories()):
        for file in [f for f in files if f.endswith(".yaml")]:
            path = os.path.join(root, file)
            try:
                with open(path) as f:
                    data = yaml.load(f.read(), Loader=yaml.SafeLoader)
                    name, _ = os.path.splitext(os.path.basename(path))
                    kind = _guess(data)
                    collection = YAML_FILES[kind]
                    if name in collection:
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

    return YAML_FILES


def get_data_entry(kind, name):
    return _load_yaml_files()[kind][name]


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
