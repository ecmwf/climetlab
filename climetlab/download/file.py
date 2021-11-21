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

    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)

    def local_path(self):

        o = urlparse(self.url)
        path = o.path

        if sys.platform == "win32" and self.url.startswith("file://"):
            # this is because urllib does not decode
            # 'file://C:\Users\name\climetlab\docs\examples\test.nc'
            # as expected.
            path = self.url[len("file://") :]

        if sys.platform == "win32" and path[0] == "/" and path[2] == ":":
            path = path[1:]

        self.path = path

        # If parts is given, we cannot use the original path
        return path if self.parts is None else None

    def prepare(self, target):
        parts = self.parts
        size = sum(p[1] for p in parts)
        return (size, "wb", 0, True)

    def transfer(self, f, pbar):
        with open(self.path, "rb") as g:
            total = 0
            for offset, length in self.parts:
                g.seek(offset)
                self.observer()
                while length > 0:
                    chunk = g.read(min(length, self.chunk_size))
                    assert chunk
                    f.write(chunk)
                    length -= len(chunk)
                    total += len(chunk)
                    pbar.update(len(chunk))
        return total
