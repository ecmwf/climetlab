# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from climetlab.readers.grib.index import JsonIndex
from climetlab.sources.indexed import IndexedSource


class IndexedUrl(IndexedSource):
    def __init__(self, url, **kwargs):

        super().__init__(JsonIndex.from_url(url), **kwargs)


source = IndexedUrl
