# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from collections import defaultdict

from .backends import JsonIndexBackend


class Index:
    def __init__(self, backend=None) -> None:
        if backend is None:
            backend = JsonIndexBackend()
        self.backend = backend


class GlobalIndex(Index):
    # index1 : 1 index, multifile.  relative path.  need baseurl.
    # index = GlobalIndex(baseurl, filename, backend=JsonIndexBackend)
    def __init__(self, index_location, baseurl, backend=None) -> None:
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
        super().__init__(backend=backend)
        self.pattern = pattern
        self.substitute_extension = substitute_extension
        self.index_extension = index_extension

    def _get_index_file(self, url):
        if self.substitute_extension:
            url = url.rsplit(".", 1)
        return url + self.index_extension
