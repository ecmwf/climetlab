# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

import cdsapi

from climetlab.normalize import normalize_args

from .base import APIKeyPrompt, FileSource

APIRC = "key: {key}\nurl: https://cds.climate.copernicus.eu/api/v2"

MESSAGE = """
An API key is needed to access this dataset. Please visit
<https://cds.climate.copernicus.eu/> to register or sign-in,
and visit <https://cds.climate.copernicus.eu/api-how-to> to
retrieve you API key.

Once this is done, please paste your key in the input field below
and press *ENTER*.
"""


class CDSAPI(APIKeyPrompt):

    text_message = MESSAGE

    markdown_message = MESSAGE

    rcfile = "~/.cdsapirc"
    prompt = "CDS api key"

    def validate(self, text):
        uid, key = text.strip().split(":")
        return APIRC.format(key="%s:%s" % (uid, key))


def client():
    try:
        return cdsapi.Client()
    except Exception as e:
        if ".cdsapirc" in str(e):
            CDSAPI().ask_user_and_save()
            return cdsapi.Client()

        raise


class CDSRetriever(FileSource):

    sphinxdoc = """
    CDSRetriever
    """

    def __init__(self, dataset, **kwargs):
        request = self.request(**kwargs)
        self.path = self.cache_file(request)
        if not os.path.exists(self.path):
            client().retrieve(dataset, request, self.path + ".tmp")
            os.rename(self.path + ".tmp", self.path)

    @normalize_args(date="date-list(%Y-%m-%d)", area="bounding-box(list)")
    def request(self, **kwargs):
        return kwargs

    def read_csv_options(self):
        return dict(
            comment="#",
            parse_dates=["report_timestamp"],
            skip_blank_lines=True,
            compression="zip",
        )


source = CDSRetriever
