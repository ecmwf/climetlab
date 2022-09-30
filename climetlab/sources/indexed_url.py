# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from climetlab.readers.grib.index import FieldsetInFilesWithSqlIndex
from climetlab.sources.indexed import IndexedSource
from climetlab.sources.indexed_urls import add_path, get_index_url


class IndexedUrl(IndexedSource):
    def __init__(
        self,
        url,
        substitute_extension=False,
        index_extension=".index",
        **kwargs,
    ):
        index = FieldsetInFilesWithSqlIndex.from_url(
            get_index_url(url, substitute_extension, index_extension),
            patch_entry=add_path(url),
        )
        super().__init__(index, **kwargs)


source = IndexedUrl
