# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import warnings

from climetlab.utils.patterns import Pattern


class GlobalIndex:
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
        # source=None,
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
        # self.source = source
        self.pattern = pattern
        self.substitute_extension = substitute_extension
        self.index_extension = index_extension
