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

from climetlab.utils import tqdm

LOG = logging.getLogger(__name__)


def _dummy_observer():
    pass


class Downloader:
    def __init__(
        self,
        url,
        chunk_size=1024 * 1024,
        timeout=None,
        parts=None,
        observer=None,
        **kwargs,
    ):
        self.url = url
        self.chunk_size = chunk_size
        self.timeout = timeout
        self.parts = parts
        self.observer = observer if observer else _dummy_observer

    def local_path(self, url):
        return None

    def extension(self, url):
        url_no_args = url.split("?")[0]
        base = os.path.basename(url_no_args)
        extensions = []
        while True:
            base, ext = os.path.splitext(base)
            if not ext:
                break
            extensions.append(ext)
        if not extensions:
            extensions.append(".unknown")
        return "".join(reversed(extensions))

    def download(self, url, target):
        if os.path.exists(target):
            return

        download = target + ".download"
        LOG.info("Downloading %s", url)

        size, mode, skip, encoded = self.prepare(url, download)

        with tqdm(
            total=size,
            initial=skip,
            unit_scale=True,
            unit_divisor=1024,
            unit="B",
            disable=False,
            leave=False,
            desc=self.title(url),
        ) as pbar:

            with open(download, mode) as f:
                total = self.transfer(f, pbar, self.observer)

            pbar.close()

        if not encoded and size is not None:
            assert (
                os.path.getsize(download) == size
            ), f"File size mismatch {os.path.getsize(download)} bytes instead of {size}"

        os.rename(download, target)

        self.finalise()
        return total

    def finalise(self):
        pass

    def title(self, url):
        return os.path.basename(url)

    def cache_data(sel, url):
        return None

    def out_of_date(self, url, path, cache_data):
        return False
