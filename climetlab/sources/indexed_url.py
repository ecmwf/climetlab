# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import warnings

from climetlab import load_source
from climetlab.core.statistics import record_statistics
from climetlab.indexing import PerUrlIndex
from climetlab.sources import Source
from climetlab.readers.grib.index import JsonIndex, SqlIndex
from climetlab.sources.indexed import IndexedSource

from .multi import MultiSource


class IndexedUrl(IndexedSource):
    def __init__(
        self,
        url,
        *args,
        base_url=None,
        index_type="json",
        db_path=None,
        filter=None,
        merger=None,
        force=None,
        **kwargs,
    ):
        self.url = url

        IndexClass = {
            "sql": SqlIndex,
            "json": JsonIndex,
        }[index_type]
        extension = {"sql": ".db", "json": ".json"}[index_type]

        if db_path is not None and os.path.exists(db_path):
            index = IndexClass.from_file(db_path)
        else:
            index = IndexClass.from_url(url, db_path=db_path)

        super().__init__(index, **kwargs)

        # sources = []
        # for url, parts in per_url_iterator:
        #     source = load_source(
        #         "url",
        #         url=url,
        #         parts=parts,
        #         filter=filter,
        #         merger=merger,
        #         force=force,
        #         # Load lazily so we can do parallel downloads
        #         # lazily=True,
        #         **kwargs,
        #     )
        #     sources.append(source)
        # if not sources:
        #     raise ValueError("Empty request: no match.")

        # super().__init__(sources, filter=filter, merger=merger)


source = IndexedUrl
