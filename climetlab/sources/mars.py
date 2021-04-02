# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import os

import ecmwfapi

from climetlab.normalize import normalize_args

from .base import APIKeyPrompt, FileSource


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
        request = self.request(**kwargs)
        self.path = self.cache_file(request)
        if not os.path.exists(self.path):
            service("mars").execute(request, self.path + ".tmp")
            os.rename(self.path + ".tmp", self.path)

    @normalize_args(
        param="variable-list(mars)",
        date="date-list(%Y-%m-%d)",
        area="bounding-box(list)",
    )
    def request(self, **kwargs):
        return kwargs

    def read_csv_options(self):
        return dict(
            sep="\t",
            comment="#",
            # parse_dates=["report_timestamp"],
            skip_blank_lines=True,
            skipinitialspace=True,
            compression="zip",
        )


source = MARSRetriever
