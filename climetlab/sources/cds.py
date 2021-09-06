# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import cdsapi

from climetlab.core.thread import SoftThreadPool
from climetlab.normalize import normalize_args
from climetlab.utils import tqdm

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

    def __init__(self, dataset, *args, **kwargs):
        assert isinstance(dataset, str)
        if len(args):
            assert len(args) == 1
            assert isinstance(args[0], dict)
            assert not kwargs
            kwargs = args[0]

        requests = self.requests(**kwargs)

        client()  # Trigger password prompt before thraeding

        nthreads = min(self.settings("number-of-download-threads"), len(requests))

        if nthreads < 2:
            self.path = [self._retrieve(dataset, r) for r in requests]
        else:
            with SoftThreadPool(nthreads=nthreads) as pool:

                futures = [pool.submit(self._retrieve, dataset, r) for r in requests]

                iterator = (f.result() for f in futures)
                self.path = list(tqdm(iterator, leave=True, total=len(requests)))

    def _retrieve(self, dataset, request):
        def retrieve(target, args):
            client().retrieve(args[0], args[1], target)

        return self.cache_file(
            retrieve,
            (dataset, request),
            extension=EXTENSIONS.get(request.get("format"), ".cache"),
        )

    @normalize_args(date="date-list(%Y-%m-%d)", area="bounding-box(list)")
    def requests(self, **kwargs):
        split_on = kwargs.pop("split_on", None)
        if split_on is None or not isinstance(kwargs.get(split_on), (list, tuple)):
            return [kwargs]

        result = []

        for v in kwargs[split_on]:
            r = dict(**kwargs)
            r[split_on] = v
            result.append(r)

        return result

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
