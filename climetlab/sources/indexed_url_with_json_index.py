# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from climetlab.readers.grib.index import FieldsetInFilesWithJsonIndex
from climetlab.sources.indexed import IndexedSource


class IndexedUrlWithJsonIndex(IndexedSource):
    # This class is mostly for testing purposes
    # sql indexing is usually better than json indexing.
    def __init__(self, url, **kwargs):
        index = FieldsetInFilesWithJsonIndex.from_url(url)
        super().__init__(index, **kwargs)


source = IndexedUrlWithJsonIndex
