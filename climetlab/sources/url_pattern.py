# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from concurrent.futures import ThreadPoolExecutor

try:
    import ipywidgets  # noqa
    from tqdm.auto import tqdm
except ImportError:
    from tqdm import tqdm

from climetlab.utils.patterns import Pattern

from .multi import MultiSource
from .url import Url


class UrlPattern(MultiSource):
    def __init__(self, pattern, *args, merger=None, **kwargs):
        urls = Pattern(pattern).substitute(*args, **kwargs)
        if not isinstance(urls, list):
            urls = [urls]

        def url_to_source(url):
            return Url(url)

        with ThreadPoolExecutor(
            max_workers=self.settings("number-of-download-threads")
        ) as executor:
            futures = executor.map(url_to_source, urls)
            sources = list(tqdm(futures, leave=True, total=len(urls)))

        super().__init__(sources, merger=merger)


source = UrlPattern
