# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.readers.netcdf.fieldset import NetCDFFieldSetFromURL
from climetlab.sources import Source


class OpenDAP(Source):
    def __init__(self, url):
        self.url = url

    def mutate(self):
        return NetCDFFieldSetFromURL(self.url)


source = OpenDAP
