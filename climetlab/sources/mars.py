# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json

import ecmwfapi

from climetlab.core.thread import SoftThreadPool
from climetlab.normalize import normalize_args
from climetlab.utils import tqdm

from .file import FileSource
from .prompt import APIKeyPrompt


class MARSAPI(APIKeyPrompt):

    text_message = """
An API key is needed to access this dataset. Please visit
https://apps.ecmwf.int/registration/ to register or sign-in
at https://www.ecmwf.int/user/login/sso
then visit https://api.ecmwf.int/v1/key/ to
retrieve you API key.

Once this is done, please copy the text that look like:

{
    "url"   : "https://api.ecmwf.int/v1",
    "key"   : "xxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "email" : "john.doe@example.com"
}

paste it the input field below and press ENTER.
"""

    markdown_message = """
An API key is needed to access this dataset. Please visit
<https://apps.ecmwf.int/registration/> to register or sign-in
at <https://www.ecmwf.int/user/login/sso>
then visit <https://api.ecmwf.int/v1/key/> to
retrieve you API key.

Once this is done, please copy the text that look like:

<pre>
{
    "url"   : "https://api.ecmwf.int/v1",
    "key"   : "xxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "email" : "john.doe@example.com"
}
</pre>

paste it the input field below and press *ENTER*.
"""

    rcfile = "~/.ecmwfapirc"
    prompt = "ECMWF api configuration"

    def validate(self, text):
        return json.dumps(json.loads(text), indent=4)


def service(name):
    try:
        return ecmwfapi.ECMWFService(name)
    except Exception as e:
        if ".ecmwfapirc" in str(e):
            MARSAPI().ask_user_and_save()
            return ecmwfapi.ECMWFService(name)

        raise


class MARSRetriever(FileSource):
    def __init__(self, **kwargs):

        requests = self.requests(**kwargs)

        service("mars")  # Trigger password prompt before thraeding

        nthreads = min(self.settings("number-of-download-threads"), len(requests))

        if nthreads < 2:
            self.path = [self._retrieve(r) for r in requests]
        else:
            with SoftThreadPool(nthreads=nthreads) as pool:

                futures = [pool.submit(self._retrieve, r) for r in requests]

                iterator = (f.result() for f in futures)
                self.path = list(tqdm(iterator, leave=True, total=len(requests)))

    def _retrieve(self, request):
        def retrieve(target, request):
            service("mars").execute(request, target)

        return self.cache_file(
            retrieve,
            request,
        )

    @normalize_args(
        param="variable-list(mars)",
        date="date-list(%Y-%m-%d)",
        area="bounding-box(list)",
    )
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
            sep="\t",
            comment="#",
            # parse_dates=["report_timestamp"],
            skip_blank_lines=True,
            skipinitialspace=True,
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


source = MARSRetriever
