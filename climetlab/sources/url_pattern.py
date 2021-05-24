# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from queue import Queue
from threading import Thread

from climetlab.utils.patterns import Pattern

from .multi import MultiSource
from .url import Url


class Worker(Thread):
    def __init__(self, tasks, sources):
        Thread.__init__(self)
        self.tasks = tasks
        self.sources = sources
        # TODO : Make sure the thread are stopped eventually
        self.daemon = True
        self.start()

    def run(self):
        while True:
            url = self.tasks.get()
            try:
                source = Url(url)
                self.sources.append(source)
            except Exception as e:
                # TODO add better handling of exceptions
                print(e)
            finally:
                self.tasks.task_done()


class DownloaderPool:
    def __init__(self, urls, num_threads=1):
        self.urls = urls
        self.tasks = Queue(num_threads)
        self.sources = []
        for t in range(num_threads):
            Worker(self.tasks, self.sources)

    def process_all(self):
        for url in self.urls:
            self.tasks.put(url)
        self.tasks.join()


class UrlPattern(MultiSource):
    def __init__(self, pattern, *args, merger=None, **kwargs):
        urls = Pattern(pattern).substitute(*args, **kwargs)
        if not isinstance(urls, list):
            urls = [urls]

        downloader = DownloaderPool(urls)
        downloader.process_all()
        sources = downloader.sources

        super().__init__(sources, merger=merger)


source = UrlPattern
