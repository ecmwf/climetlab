# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import warnings
from collections import defaultdict

from climetlab.sources.indexed import Index, SqlIndex
from climetlab.utils.patterns import Pattern


class GlobalIndex(SqlIndex):
    def __init__(self, index_location, baseurl) -> None:
        warnings.warn(
            "GlobalIndex is obsolete. Please update your code and use the 'directory' source"
        )
        raise NotImplementedError(
            "GlobalIndex is obsolete. Please update your code and use the 'directory' source"
        )
        """The GloblaIndex has one index managing multiple urls/files.
        This unique index is found at "index_location"
        The path of each file is written in the index as a relative path.
        It is relative to a base url: "baseurl".
        """

    # def get_path_offset_length(self, request):
    #    dic = defaultdict(list)

    #    # group parts by url
    #    for path, parts in self.sel(request):
    #        dic[path].append(parts)

    #    # and sort
    #    dic = {url: sorted(parts) for url, parts in dic.items()}

    #    urls_parts = [(k, v) for k, v in dic.items()]

    #    return urls_parts


class PerUrlIndex:
    # index2 : 1 index per url.
    #        2a: index location = url location + '.jsonl'
    #        2b: index location = url location - '.grib' + '.jsonl'
    # index = PerUrlIndex(pattern, backend=JsonIndexBackend)
    def __init__(
        self,
        pattern,
        substitute_extension=False,
        index_extension=".index",
        source=None,
    ) -> None:
        """The PerUrlIndex uses one index for each urls/files that it manages.

        The urls are built from the pattern and the request.
        For each url, the location of the index is build (then downloaded and cached)
        using the url and changing its extension into ".index".

        pattern: pattern to build the list of url.
        index_extension (".index"): extension for the index url.
        substitute_extension (False): if set to True, substitute the index_extension
        to build the index url instead of appending.
        get_path_offset_length(): get the urls and parts for a given request.
        """
        super().__init__()
        self.source = source
        self.pattern = pattern
        self.substitute_extension = substitute_extension
        self.index_extension = index_extension
        self.backends = {}

        self._indexes = {}

    def _resolve_extension(self, url):
        if callable(self.substitute_extension):
            return self.substitute_extension(url)
        if self.substitute_extension:
            url = url.rsplit(".", 1)[0]
        return url + self.index_extension

    def get_index(self, url, request):
        assert isinstance(url, str), url

        from climetlab.sources.indexed import SqlIndex

        if url in self._indexes:
            return self._indexes[url]

        index_url = self._resolve_extension(url)

        download
        index = build(url_index)

        self._indexes[url] = index_url
        # backend = SqlIndex(order=["offset"], cache_metadata=dict(index_url=index_url), )
        return self._indexes[url]

    def get_urls_parts(self, request):
        dic = defaultdict(list)

        pattern = Pattern(self.pattern, ignore_missing_keys=True)
        urls = pattern.substitute(**request)
        if not isinstance(urls, list):
            urls = [urls]

        request = dict(**request)  # deepcopy to avoid changing the user's request
        for used in pattern.names:
            # consume arguments used by Pattern to build the urls
            # This is to avoid keeping them on the request
            request.pop(used)

        # group parts by url
        raise NotImplementedError(" per_url_index_is_broken ")
        for url in urls:
            backend = self.get_index(url, initial_request)
            for _, parts in backend.sel(request):
                dic[url].append(parts)

        # and sort
        dic = {url: sorted(parts) for url, parts in dic.items()}

        urls_parts = [(k, v) for k, v in dic.items()]

        return urls_parts

    def __repr__(self) -> str:
        return f"PerUrlIndex(pattern={self.pattern})"
