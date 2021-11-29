# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os

LOG = logging.getLogger(__name__)


def _ignore(*args, **kwargs):
    pass


class NoBar:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass


class Downloader:
    def __init__(
        self,
        url,
        chunk_size=1024 * 1024,
        timeout=None,
        parts=None,
        observer=_ignore,
        statistics_gatherer=_ignore,
        progress_bar=NoBar,
        **kwargs,
    ):
        self.url = url
        self.chunk_size = chunk_size
        self.timeout = timeout
        self.parts = parts
        self.observer = observer
        self.statistics_gatherer = statistics_gatherer
        self.progress_bar = progress_bar

    def local_path(self):
        return None

    def extension(self, filename=None):
        """Return extensions:
        - from filename if not None.
        - else from self.url
        - else return ".unknonwn"
        """
        extensions = []
        if filename:
            extensions = self._extensions(filename)
        if not extensions:
            url_no_args = self.url.split("?")[0]
            extensions = self._extensions(url_no_args)
        if not extensions:
            extensions.append(".unknown")
        return "".join(reversed(extensions))

    def _extensions(self, url_or_filename):
        base = os.path.basename(url_or_filename)
        extensions = []
        while True:
            base, ext = os.path.splitext(base)
            if not ext:
                break
            extensions.append(ext)
        return extensions

    def download(self, target):
        if os.path.exists(target):
            return

        download = target + ".download"
        LOG.info("Downloading %s", self.url)

        size, mode, skip, trust_size = self.prepare(download)

        with self.progress_bar(
            total=size,
            initial=skip,
            desc=self.title(),
        ) as pbar:

            with open(download, mode) as f:
                total = self.transfer(f, pbar)

            pbar.close()

        if trust_size and size is not None:
            assert (
                os.path.getsize(download) == size
            ), f"File size mismatch {os.path.getsize(download)} bytes instead of {size}"

        os.rename(download, target)

        self.finalise()
        return total

    def finalise(self):
        pass

    def title(self):
        return os.path.basename(self.url)

    def cache_data(self):
        return None

    def out_of_date(self, path, cache_data):
        return False
