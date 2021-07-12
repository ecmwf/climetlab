
#!/usr/bin/env python3# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from __future__ import annotations

__version__ = "0.1.0"

import re

import requests

from climetlab.sources.multi_url import MultiUrl

URLPATTERN = "https://zenodo.org/api/records/{record_id}"


def DEFAULT_FILE_FILTER(path, *args, **kwargs):
    if path.endswith(".csv"):
        return True
    if path.endswith(".nc"):
        return True
    if path.endswith(".zip"):
        return True
    print(f"skipping {path} ")
    return False


class Zenodo(MultiUrl):
    def __init__(
        self,
        record_id=None,
        list_only=False,
        zenodo_file_filter=None,
        filter=DEFAULT_FILE_FILTER,
        *args,
        **kwargs,
    ):
        url = URLPATTERN.format(record_id=record_id)
        self.url = url
        r = requests.get(url)
        r.raise_for_status()
        self.json = r.json()

        zfiles = self.json["files"]

        keys = [f["key"] for f in zfiles]

        keys = []
        urls = []
        for f in zfiles:
            k = f["key"]
            if callable(zenodo_file_filter):
                if not zenodo_file_filter(k):
                    continue
            if isinstance(zenodo_file_filter, (tuple, list)):
                if not k in zenodo_file_filter:
                    continue
            if isinstance(zenodo_file_filter, str):
                if not re.match(zenodo_file_filter, k):
                    continue

            keys.append(k)
            urls.append(f["links"]["self"])

        self.list_content_keys = keys

        self.list_only = list_only
        if list_only:

            # Idea: generate csv in cache
            super().__init__([])

            print(self.list_content_keys)
            return  # Note: will mutate into Empty


        def interanl_filter(path):
            return filter(path)

        super().__init__(urls, filter=interanl_filter, *args, **kwargs)

    def mutate(self):
        if self.list_only:
            return cml.load_source("file", ...)
        return self


source = Zenodo
