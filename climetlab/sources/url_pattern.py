# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

try:
    import ipywidgets  # noqa
    from tqdm.auto import tqdm
except ImportError:
    from tqdm import tqdm


from climetlab.core.thread import SoftThreadPool
from climetlab.utils.patterns import Pattern

from .multi import MultiSource
from .url import Url


class UrlPattern(MultiSource):
    def __init__(self, pattern, *args, merger=None, **kwargs):
        urls = Pattern(pattern).substitute(*args, **kwargs)
        if not isinstance(urls, list):
            urls = [urls]

        def url_to_source(url):  # , pbar):
            # time.sleep(4)
            url = Url(url)
            #            pbar.update(1)
            return url

        nthreads = self.settings("number-of-download-threads")
        # import os
        # with tqdm(
        #     total=len(urls),
        #     disable=False,
        #     leave=False,
        #     # desc='Downloading'
        # ) as pbar:
        #     total = 0
        #     pbar.update(total)

        if nthreads < 2:
            sources = [url_to_source(url) for url in urls]
        else:
            with SoftThreadPool(nthreads=nthreads) as pool:

                futures = [pool.submit(url_to_source, url) for url in urls]

                iterator = (f.result() for f in futures)
                sources = list(tqdm(iterator, leave=True, total=len(urls)))

        super().__init__(sources, merger=merger)


source = UrlPattern
