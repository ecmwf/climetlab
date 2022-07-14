# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import warnings

from climetlab import load_source
from climetlab.core.statistics import record_statistics
from climetlab.indexing import PerUrlIndex
from climetlab.sources import Source
from climetlab.sources.indexed import IndexedSource, JsonIndex, SqlIndex

from .multi import MultiSource


class IndexedUrls(MultiSource):
    def __init__(
        self,
        index,
        request,
        *args,
        baseurl=None,
        filter=None,
        merger=None,
        force=None,
        **kwargs,
    ):
        if isinstance(index, PerUrlIndex):
            warnings.warn(
                "Passing a PerUrlIndex object is obsolete, please update your code."
            )
            index.source = self
        else:
            raise ValueError(
                "Source 'indexed-url' is deprecated. Use source 'remote-indexed' instead..."
            )

        per_url_iterator = index.get_urls_parts(request)

        record_statistics(
            "indexed-urls",
            request=str(request),
        )

        sources = []
        for url, parts in per_url_iterator:
            source = load_source(
                "url",
                url=url,
                parts=parts,
                filter=filter,
                merger=merger,
                force=force,
                # Load lazily so we can do parallel downloads
                # lazily=True,
                **kwargs,
            )
            sources.append(source)
        if not sources:
            raise ValueError("Empty request: no match.")

        super().__init__(sources, filter=filter, merger=merger)


source = IndexedUrls
