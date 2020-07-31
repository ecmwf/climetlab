# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import ecmwfapi
import os
import sys
import json
import getpass

from climetlab.core.caching import temp_file
from .base import FileSource

MESSAGE = """

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

paste it the input field below and press <return>.

"""


def service(name):
    try:
        return ecmwfapi.ECMWFService(name)
    except Exception as e:
        if ".ecmwfapirc" in str(e):
            print(str(e) + "\n" + MESSAGE, file=sys.stderr)
            cfg = json.loads(getpass.getpass("ECMWF api configuration: "))
            with open(os.path.expanduser("~/.ecmwfapirc"), "w") as f:
                print(json.dumps(cfg, indent=4), file=f)
            return ecmwfapi.ECMWFService(name)
        else:
            raise


class MARSRetriever(FileSource):

    def __init__(self, **req):
        self.path = temp_file('MARSRetriever', req)
        if not os.path.exists(self.path):
            service('mars').execute(req, self.path + '.tmp')
            os.rename(self.path + '.tmp', self.path)


source = MARSRetriever
