# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import cdsapi

from climetlab.normalize import normalize_args

from .file import FileSource
from .prompt import APIKeyPrompt

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


EXTENSIONS = {
    "grib": ".grib",
    "netcdf": ".nc",
}


class CDSRetriever(FileSource):

    sphinxdoc = """
    CDSRetriever
    """

    def __init__(self, dataset, **kwargs):
        request = self.request(**kwargs)

        def retrieve(target, args):
            client().retrieve(args[0], args[1], target)

        self.path = self.cache_file(
            retrieve,
            (dataset, request),
            extension=EXTENSIONS.get(request.get("format"), ".cache"),
        )

    @normalize_args(date="date-list(%Y-%m-%d)", area="bounding-box(list)")
    def request(self, **kwargs):
        return kwargs

    def to_pandas(self, **kwargs):
        pandas_read_csv_kwargs = dict(
            comment="#",
            parse_dates=["report_timestamp"],
            skip_blank_lines=True,
            compression="zip",
        )

        pandas_read_csv_kwargs.update(kwargs.get("pandas_read_csv_kwargs", {}))

        odc_read_odb_kwargs = dict(
            # TODO
        )

        odc_read_odb_kwargs.update(kwargs.get("odc_read_odb_kwargs", {}))

        return super().to_pandas(
            pandas_read_csv_kwargs=pandas_read_csv_kwargs,
            odc_read_odb_kwargs=odc_read_odb_kwargs,
            **kwargs,
        )


source = CDSRetriever
