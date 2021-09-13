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
import time
import urllib

import requests

from climetlab import load_source

from .multi import MultiSource
from .prompt import APIKeyPrompt

# See https://eumetsatspace.atlassian.net/wiki/spaces/DSDS/pages/315818088/Using+the+APIs


class EumetsatAPI(APIKeyPrompt):

    text_message = """
An API key is needed to access this dataset. Please visit
https://eoportal.eumetsat.int/ to register or sign-in
then visit TODO to
retrieve you API key.

Once this is done, please copy the text that look like:

{
   "consumer_key":    "xxxxxxxxxxx",
   "consumer_secret": "xxxxxxxxxxx"
}

paste it the input field below and press ENTER.
"""

    markdown_message = """
An API key is needed to access this dataset. Please visit
<https://eoportal.eumetsat.int/> to register or sign-in
then visit <https://TODO> to
retrieve you API key.

Once this is done, please copy the text that look like:

<pre>
{
   "consumer_key":    "xxxxxxxxxxx",
   "consumer_secret": "xxxxxxxxxxx"
}
</pre>

paste it the input field below and press *ENTER*.
"""

    rcfile = "~/.eumetsatapirc"
    prompt = "EUMETSAT api configuration"

    def validate(self, text):
        return json.dumps(json.loads(text), indent=4)


class Token:
    def __init__(self):
        with open(os.path.expanduser("~/.eumetsatapirc")) as f:
            self._credentials = json.loads(f.read())

        self._token = {"expires_in": 0}
        self._last = 0

    @property
    def token(self):

        now = time.time()
        if now - self._last > self._token["expires_in"] - 10:

            r = requests.post(
                "https://api.eumetsat.int/token",
                data={"grant_type": "client_credentials"},
                auth=requests.auth.HTTPBasicAuth(
                    self._credentials["consumer_key"],
                    self._credentials["consumer_secret"],
                ),
            )

            r.raise_for_status()

            self._last = now
            self._token = r.json()

        return self._token["access_token"]

    def __repr__(self):
        return self.token


# Try with EO:EUM:DAT:METOP:GLB-SST-NC


class Client:
    def __init__(self):
        self.token = Token()

    def features(
        self,
        collection_id,
        start_date=None,
        end_date=None,
        polygon=None,
    ):
        query = {
            "format": "json",
            "pi": collection_id,
        }

        if start_date is not None:
            query["dtstart"] = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if end_date is not None:
            query["dtend"] = end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if polygon is not None:
            geo = ",".join([f"{pt[0]} {pt[1]}" for pt in polygon])
            query["geo"] = f"POLYGON(({geo}))"

        search_url = "https://api.eumetsat.int/data/search-products/os"

        query["si"] = 0
        query["c"] = 1000

        while True:

            r = requests.get(search_url, query)
            r.raise_for_status()
            result = r.json()

            features = result["features"]

            if not features:
                break

            yield from features

            query["si"] += len(features)

    def products(self, *args, **kwargs):
        for feature in self.features(*args, **kwargs):
            pid = urllib.parse.quote(feature["properties"]["identifier"])
            cid = urllib.parse.quote(feature["properties"]["parentIdentifier"])
            url = f"https://api.eumetsat.int/data/download/collections/{cid}/products/{pid}"
            size = feature["properties"]["productInformation"]["size"]
            # print(json.dumps(feature, indent=4))
            # break
            return load_source(
                "url",
                url,
                http_headers={"Authorization": f"Bearer {self.token}"},
                fake_headers={
                    "content-length": size * 1024,
                    "content-encoding": "unknown",
                },
            )


def client():
    try:
        return Client()
    except Exception as e:
        if ".eumetsatapirc" in str(e):
            EumetsatAPI().ask_user_and_save()
            return Client()

        raise


class EumetsatRetriever(MultiSource):
    def __init__(self, collection_id, *args, **kwargs):
        assert isinstance(collection_id, str)

        c = client()
        super().__init__(c.products(collection_id), *args, **kwargs)


source = EumetsatRetriever
