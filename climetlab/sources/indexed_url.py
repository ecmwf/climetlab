# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from climetlab.readers.grib.index import JsonIndex, SqlIndex
from climetlab.sources.indexed import IndexedSource


class IndexedUrl(IndexedSource):
    def __init__(self, url, _index_type="sql", **kwargs):

        index_class = dict(json=JsonIndex, sql=SqlIndex)[_index_type]
        index = index_class.from_url(url)
        super().__init__(index, **kwargs)
        # assert isinstance(self.index, index_class), self.index


source = IndexedUrl
