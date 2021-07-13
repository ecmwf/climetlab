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

from climetlab.sources.url import Url
from climetlab.utils import get_json

LOG = logging.getLogger(__name__)
URLPATTERN = "https://zenodo.org/api/records/{record_id}"


class Zenodo(Url):
    def __init__(
        self,
        record_id,
        file_key=None,
        filter=None,
        merger=None,
        *args,
        **kwargs,
    ):

        record = get_json(URLPATTERN.format(record_id=record_id))
        LOG.debug("ZENODO record %s", json.dumps(record, indent=4, sort_keys=True))

        urls = {}
        for file in record["files"]:
            urls[file["key"]] = file["links"]["self"]

        if file_key is None:
            if len(urls) != 1:
                raise ValueError(
                    f"No `file_key` given, please specify on of {sorted(urls.keys())}"
                )
            file_key = list(urls.keys())[0]

        if file_key not in urls:
            raise ValueError(
                f"Invalid zenodo key '{file_key}', values are {sorted(urls.keys())}"
            )

        LOG.debug("ZENODO record_keys %s", sorted(urls.keys()))

        LOG.debug("ZENODO url %s", urls[file_key])
        super().__init__(
            urls[file_key],
            filter=filter,
            merger=merger,
            *args,
            **kwargs,
        )


source = Zenodo
