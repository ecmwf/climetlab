# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.sources.multi_url import MultiUrl
from climetlab.utils.patterns import Pattern


class UrlPattern(MultiUrl):
    def __init__(self, pattern, *args, filter=None, merger=None, force=False, **kwargs):
        urls = Pattern(pattern).substitute(*args, **kwargs)
        super().__init__(
            urls, *args, filter=filter, merger=merger, force=force, **kwargs
        )


source = UrlPattern
