# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# WIP.

import json
import os

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# import climetlab as cml

# Your client credentials
with open(os.path.expanduser("~/.sentinelhubrc")) as f:
    credentials = json.loads(f.read())
client_id = credentials["client_id"]
client_secret = credentials["client_secret"]

# Create a session
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)


# Get token for the session
token = oauth.fetch_token(
    token_url="https://services.sentinel-hub.com/oauth/token",
    client_id=client_id,
    client_secret=client_secret,
)

# All requests using this session will have an access token automatically added
resp = oauth.get("https://services.sentinel-hub.com/oauth/tokeninfo")
print(resp.content)
