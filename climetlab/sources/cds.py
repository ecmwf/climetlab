# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import cdsapi
import yaml

from climetlab.core.thread import SoftThreadPool
from climetlab.decorators import normalize
from climetlab.utils import tqdm

from .file import FileSource
from .prompt import APIKeyPrompt


class CDSAPIKeyPrompt(APIKeyPrompt):
    register_or_sign_in_url = "https://cds.climate.copernicus.eu/"
    retrieve_api_key_url = "https://cds.climate.copernicus.eu/api-how-to"

    prompts = [
        dict(
            name="url",
            default="https://cds.climate.copernicus.eu/api/v2",
            title="API url",
            validate=r"http.?://.*",
        ),
        dict(
            name="key",
            example="123:abcdef01-0000-1111-2222-0123456789ab",
            title="API key",
            hidden=True,
            validate=r"\d+:[\-0-9a-f]+",
        ),
    ]

    rcfile = "~/.cdsapirc"

    def save(self, input, file):
        yaml.dump(input, file, default_flow_style=False)


def client():
    prompt = CDSAPIKeyPrompt()
    prompt.check()

    try:
        return cdsapi.Client()
    except Exception as e:
        if ".cdsapirc" in str(e):
            prompt.ask_user_and_save()
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
        super().__init__()

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

    @normalize("date", "date-list(%Y-%m-%d)")
    @normalize("area", "bounding-box(list)")
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
