# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import sys
from urllib.parse import urlparse

from .downloader import Downloader

LOG = logging.getLogger(__name__)


class FileDownloader(Downloader):
    supports_parts = True

    def local_path(self, url):

        o = urlparse(url)
        path = o.path

        if sys.platform == "win32" and url.startswith("file://"):
            # this is because urllib does not decode
            # 'file://C:\Users\name\climetlab\docs\examples\test.nc'
            # as expected.
            path = url[len("file://") :]

        if sys.platform == "win32" and path[0] == "/" and path[2] == ":":
            path = path[1:]

        self.path = path

        # If parts is given, we cannot use the original path
        return path if self.owner.parts is None else None

    def prepare(self, url, download):
        parts = self.owner.parts
        size = sum(p[1] for p in parts)
        mode = "wb"
        skip = 0
        encoded = None
        return size, mode, skip, encoded

    def transfer(self, f, pbar, watcher):
        with open(self.path, "rb") as g:
            total = 0
            for offset, length in self.owner.parts:
                g.seek(offset)
                watcher()
                while length > 0:
                    chunk = g.read(min(length, self.owner.chunk_size))
                    assert chunk
                    f.write(chunk)
                    length -= len(chunk)
                    total += len(chunk)
                    pbar.update(len(chunk))
        return total
