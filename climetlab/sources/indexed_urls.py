# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import warnings

from climetlab.core.index import MultiIndex
from climetlab.indexing import PerUrlIndex
from climetlab.readers.grib.index import JsonIndex
from climetlab.sources.indexed import IndexedSource
from climetlab.utils.patterns import Pattern


class IndexedUrls(IndexedSource):
    def __init__(
        self,
        pattern,
        request,
        substitute_extension=False,
        index_extension=".index",
        **kwargs,
    ):
        if isinstance(pattern, PerUrlIndex):
            warnings.warn(
                "Passing a PerUrlIndex object is obsolete, please update your code."
            )
            substitute_extension = pattern.substitute_extension
            index_extension = pattern.index_extension
            pattern = pattern.pattern

        print("PATTERN", pattern)
        pattern = Pattern(pattern, ignore_missing_keys=True)
        urls = pattern.substitute(**request)
        if not isinstance(urls, list):
            urls = [urls]

        request = dict(**request)  # deepcopy to avoid changing the user's request
        for used in pattern.names:
            # consume arguments used by Pattern to build the urls
            # This is to avoid keeping them on the request
            request.pop(used)

        def add_path(url):
            def wrapped(entry):
                entry["_url"] = url
                entry.pop("_path", None)

            return wrapped

        index = MultiIndex(
            JsonIndex.from_url(
                url + index_extension,
                selection=request,
                patch_entry=add_path(url),
            )
            for url in urls
        )

        super().__init__(index, **kwargs)


source = IndexedUrls
