# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import warnings

from climetlab.indexing import PerUrlIndex
from climetlab.readers.grib.index import FieldsetInFilesWithSqlIndex, MultiFieldSet
from climetlab.sources.indexed import IndexedSource
from climetlab.utils.patterns import Pattern


def get_index_url(url, substitute_extension, index_extension):
    if substitute_extension:
        url = ".".join(".".split(url)[:-1])

    if callable(index_extension):
        return index_extension(url)
    return url + index_extension


def add_path(url):
    def wrapped(entry):
        entry["_path"] = url
        return entry

    return wrapped


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

        index = MultiFieldSet(
            FieldsetInFilesWithSqlIndex.from_url(
                get_index_url(url, substitute_extension, index_extension),
                selection=request,
                patch_entry=add_path(url),
            )
            for url in urls
        )

        super().__init__(index, **kwargs)


source = IndexedUrls
