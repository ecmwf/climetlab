# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import xarray as xr

from .base import Source


class OpenDAP(Source):
    def __init__(self, url):
        super().__init__()

        self.url = url

    def to_xarray(self):
        return xr.open_dataset(self.url)


source = OpenDAP
