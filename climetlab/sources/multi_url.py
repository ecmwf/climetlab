# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab import load_source

from .multi import MultiSource


class MultiUrl(MultiSource):
    def __init__(self, urls, *args, filter=None, merger=None, force=None, **kwargs):
        if not isinstance(urls, (list, tuple)):
            urls = [urls]

        # if filter is not None:
        #     urls = [url for url in urls if filter(url)]

        assert len(urls)

        sources = [
            load_source(
                "url",
                url,
                filter=filter,
                merger=merger,
                force=force,
                # Load lazily so we can do parallel downloads
                lazily=True,
            )
            for url in sorted(urls)
        ]

        super().__init__(sources, filter=filter, merger=merger)
