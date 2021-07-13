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

import json
import logging

from climetlab.sources.multi_url import MultiUrl
from climetlab.utils import get_json

LOG = logging.getLogger(__name__)
URLPATTERN = "https://zenodo.org/api/records/{record_id}"


class Zenodo(MultiUrl):
    def __init__(
        self,
        record_id,
        key=None,
        keys=None,
        filter=None,
        merger=None,
        *args,
        **kwargs,
    ):

        record = get_json(URLPATTERN.format(record_id=record_id))
        LOG.debug("ZENODO record %s", json.dumps(record, indent=4, sort_keys=True))

        record_keys = set()
        for file in record["files"]:
            record_keys.add(file["key"])

        user_keys = set()
        if key is not None:
            user_keys.add(key)

        if keys is not None:
            for key in keys:
                user_keys.add(key)

        if len(user_keys) == 0:
            user_keys = record_keys

        for key in user_keys:
            if key not in record_keys:
                raise ValueError(
                    f"Invalid zenodo key '{key}', values are {sorted(record_keys)}"
                )

        LOG.debug("ZENODO record_keys %s", record_keys)
        LOG.debug("ZENODO user_keys %s", user_keys)
        urls = [
            file["links"]["self"]
            for file in record["files"]
            if file["key"] in user_keys
        ]

        LOG.debug("ZENODO urls %s", urls)
        super().__init__(urls, filter=filter, merger=merger, *args, **kwargs)


source = Zenodo
