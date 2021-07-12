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


def filter_builder(filter):
    if callable(filter):

        def _filter(k):
            print(f"checking {k}")
            return filter(k)

        return _filter
    if isinstance(filter, (tuple, list)):

        def _filter(k):
            print(f"checking {k}")
            return k in filter

        return _filter
    if isinstance(filter, str):

        def _filter(k):
            f = re.match(filter, k)
            print(f"checking {k} with {filter}: {f}")
            return f

        return _filter
    raise ValueError(f"Wrong input of type {type(filter)} for filter={filter}")


class Zenodo(MultiUrl):
    def __init__(
        self,
        record_id=None,
        list_only=False,
        filter=DEFAULT_FILE_FILTER,
        *args,
        **kwargs,
    ):
        self.list_only = list_only
        _filter = filter_builder(filter)

        url = URLPATTERN.format(record_id=record_id)
        self.url = url
        r = requests.get(url)
        r.raise_for_status()
        self.json = r.json()

        files = self.json["files"]

        keys = [f["key"] for f in files]

        urls = []
        for f in files:
            urls.append(f["links"]["self"])
        keys = []

        for f in files:
            k = f["key"]
            print(k)
            if _filter(k):
                print(f"Appending {k}")
                keys.append(k)
            else:
                print(f"Skipping {k}")
        self.list_content_keys = keys

        if list_only:
            # Idea: generate csv in cache
            # super().__init__([])
            print(self.list_content_keys)
            return  # Note: will mutate into a csv File

        print(urls)
        super().__init__(urls, filter=_filter, *args, **kwargs)

    def mutate(self):
        if self.list_only:
            # create csv file in cache and
            return cml.load_source("file", ...)
        return self


source = Zenodo
