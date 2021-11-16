# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from collections import defaultdict

from climetlab import load_source
from climetlab.utils.patterns import Pattern

from .backends import JsonIndexBackend


class Index:
    def __init__(self, backend=None) -> None:
        if backend is None:
            backend = JsonIndexBackend()
        self.backend = backend


class GlobalIndex(Index):
    def __init__(self, index_location, baseurl, backend=None) -> None:
        """The GloblaIndex has one index managing multiple urls/files.
        This unique index is found at "index_location"
        The path of each file is written in the index as a relative path.
        It is relative to a base url: "baseurl".
        """

        super().__init__(backend=backend)
        self.baseurl = baseurl
        # if is url index_location
        #   download index_location
        self.backend.add_index_file(index_location)

    def lookup_request(self, request):
        dic = defaultdict(list)

        # group parts by url
        for path, parts in self.backend.lookup(request):
            url = f"{self.baseurl}/{path}"
            dic[url].append(parts)

        # and sort
        dic = {k: sorted(v) for k, v in dic.items()}

        urls_parts = [(k, v) for k, v in dic.items()]

        return urls_parts


class PerUrlIndex(Index):  # TODO
    # index2 : 1 index per url.
    #        2a: index location = url location + '.jsonl'
    #        2b: index location = url location - '.grib' + '.jsonl'
    # index = PerUrlIndex(pattern, backend=JsonIndexBackend)
    def __init__(
        self,
        pattern,
        backend=None,
        substitute_extension=False,
        index_extension=".index",
    ) -> None:
        """The PerUrlIndex uses one index for each urls/files that it manages.
        The urls/files are built from the pattern and the request.
        The indexese locations are built from each url.
        """
        super().__init__(backend=backend)
        self.pattern = pattern
        self.substitute_extension = substitute_extension
        self.index_extension = index_extension
        self._backends = {}

    def _build_index_file(self, url):
        if self.substitute_extension:
            url = url.rsplit(".", 1)[0]
        return url + self.index_extension

    def get_backend(self, url):
        if url in self._backends:
            return self._backends[url]

        index_url = self._build_index_file(url)
        index_source = load_source("url", index_url)
        index_filename = index_source.path
        backend = JsonIndexBackend()
        backend.add_index_file(index_filename)

        self._backends[url] = backend
        return self._backends[url]

    def lookup_request(self, request):
        dic = defaultdict(list)

        pattern = Pattern(self.pattern, ignore_missing_keys=True)
        urls = pattern.substitute(**request)
        for used in pattern.names:
            # consume arguments used by Pattern to build the urls
            # This is to avoid keeping them on the request
            request.pop(used)

        # group parts by url
        for url in urls:
            backend = self.get_backend(url)
            for path, parts in backend.lookup(request):
                dic[url].append(parts)

        # and sort
        dic = {k: sorted(v) for k, v in dic.items()}

        urls_parts = [(k, v) for k, v in dic.items()]

        return urls_parts
