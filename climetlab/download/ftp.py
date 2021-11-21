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
from ftplib import FTP
from urllib.parse import urlparse

from .downloader import Downloader

LOG = logging.getLogger(__name__)


class FTPDownloaderBase(Downloader):

    supports_parts = False

    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)

    def prepare(self, target):

        o = urlparse(self.url)
        assert o.scheme == "ftp"

        if "@" in o.netloc:
            auth, server = o.netloc.split("@")
            user, password = auth.split(":")
        else:
            auth, server = None, o.netloc
            user, password = "anonymous", "anonymous"

        ftp = FTP(
            server,
            timeout=self.timeout,
        )

        if auth:
            ftp.login(user, password)
        else:
            ftp.login()

        ftp.cwd(os.path.dirname(o.path))
        ftp.set_pasv(True)
        self.filename = os.path.basename(o.path)
        self.ftp = ftp

        return (ftp.size(self.filename), "wb", 0, True)

    def transfer(self, f, pbar):
        total = 0

        def callback(chunk):
            nonlocal total
            self.observer()
            f.write(chunk)
            total += len(chunk)
            pbar.update(len(chunk))

        self.ftp.retrbinary(f"RETR {self.filename}", callback)

    def finalise(self):
        self.ftp.close()


class FullFTPDownloader(FTPDownloaderBase):
    pass


class PartFTPDownloader(FTPDownloaderBase):
    def __init__(self, url, **kwargs):
        # If needed, that can be implemented with the PartFilter
        raise NotImplementedError("Part FTPDownloader is not yet implemented")
