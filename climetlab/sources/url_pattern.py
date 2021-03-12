# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.utils.patterns import Pattern

from .multi import MultiSource
from .url import Url


class UrlPattern(MultiSource):
    def __init__(self, pattern, *args, **kwargs):
        urls = Pattern(pattern).substitute(*args, **kwargs)
        if not isinstance(urls, list):
            urls = [urls]

        sources = [Url(url) for url in urls]
        super().__init__(sources)


source = UrlPattern
