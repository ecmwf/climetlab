# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import cdsapi
import os
import sys

from .base import FileSource
from climetlab.core.caching import temp_file
import getpass


MESSAGE = """{error}

An API key is needed to access this dataset. Please visit
https://cds.climate.copernicus.eu/ to register or sign-in,
and visit https://cds.climate.copernicus.eu/api-how-to to
retrieve you API key.

Once this is done, please paste your key in the input field below
and press <return>.

"""

APIRC = "key: {key}\nurl: https://cds.climate.copernicus.eu/api/v2"


def client():
    try:
        return cdsapi.Client()
    except Exception as e:
        if str(e).endswith(".cdsapirc"):
            print(MESSAGE.format(error=str(e)), file=sys.stderr)
            key = getpass.getpass("CDS api key: ")
            with open(os.path.expanduser("~/.cdsapirc"), "w") as f:
                print(APIRC.format(key=key), file=f)
            return cdsapi.Client()
        else:
            raise


class CDSRetriever(FileSource):

    sphinxdoc = '''
    CDSRetriever
    '''

    def __init__(self, dataset, **req):
        self.path = temp_file('CDSRetriever', req)
        if not os.path.exists(self.path):
            client().retrieve(dataset, req, self.path + '.tmp')
            os.rename(self.path + '.tmp', self.path)


source = CDSRetriever
