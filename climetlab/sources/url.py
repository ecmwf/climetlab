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
import shutil
from ftplib import FTP
from urllib.parse import urlparse

import requests

from climetlab.core.settings import SETTINGS

try:
    import ipywidgets  # noqa
    from tqdm.auto import tqdm
except ImportError:
    from tqdm import tqdm

from .base import FileSource

LOG = logging.getLogger(__name__)


def dummy():
    pass


class Downloader:
    def __init__(self, owner):
        self.owner = owner

    def download(self, url, target):
        if os.path.exists(target):
            return

        download = target + ".download"
        LOG.info("Downloading %s", url)

        size = self.prepare(url)

        mode = "wb"
        with tqdm(
            total=size,
            unit_scale=True,
            unit_divisor=1024,
            unit="B",
            disable=False,
            leave=False,
            desc=os.path.basename(url),
        ) as pbar:

            with open(download, mode) as f:
                total = self.transfer(f, pbar, self.owner.watcher)

            pbar.close()

        # take care of race condition when two processes
        # download into the same file at the same time
        try:
            os.rename(download, target)
        except FileNotFoundError as e:
            if not os.path.exists(target):
                raise e

        self.finalise()
        return total

    def finalise(self):
        pass


class HTTPDownloader(Downloader):
    def prepare(self, url):

        r = requests.head(url, verify=self.owner.verify)
        r.raise_for_status()
        try:
            size = int(r.headers["content-length"])
        except Exception:
            size = None
        r = requests.get(
            url,
            stream=True,
            verify=self.owner.verify,
            timeout=SETTINGS.as_seconds("url-download-timeout"),
        )
        r.raise_for_status()

        self.request = r

        return size

    def transfer(self, f, pbar, watcher):
        total = 0
        for chunk in self.request.iter_content(chunk_size=1024 * 1024):
            watcher()
            if chunk:
                f.write(chunk)
                total += len(chunk)
                pbar.update(len(chunk))
        return total


class FTPDownloader(Downloader):
    def prepare(self, url):

        o = urlparse(url)
        assert o.scheme == "ftp"

        if "@" in o.netloc:
            auth, server = o.netloc.split("@")
            user, password = auth.split(":")
        else:
            auth, server = None, o.netloc
            user, password = "anonymous", "anonymous"

        ftp = FTP(
            server,
            timeout=SETTINGS.as_seconds("url-download-timeout"),
        )

        if auth:
            ftp.login(user, password)
        else:
            ftp.login()

        ftp.cwd(os.path.dirname(o.path))
        ftp.set_pasv(True)
        self.filename = os.path.basename(o.path)
        self.ftp = ftp
        return ftp.size(self.filename)

    def transfer(self, f, pbar, watcher):
        total = 0

        def callback(chunk):
            nonlocal total
            watcher()
            f.write(chunk)
            total += len(chunk)
            pbar.update(len(chunk))

        self.ftp.retrbinary(f"RETR {self.filename}", callback)

    def finalise(self):
        self.ftp.close()


class FileDownloader(Downloader):
    def download(self, url, target):
        o = urlparse(url)
        assert os.path.exists(o.path), f"File not found: {o.path}"
        os.symlink(o.path, target)


DOWNLOADERS = dict(
    ftp=FTPDownloader,
    http=HTTPDownloader,
    https=HTTPDownloader,
    file=FileDownloader,
)


class Url(FileSource):
    def __init__(
        self,
        url,
        unpack=None,
        verify=True,
        watcher=None,
        force=False,
        **kwargs,
    ):
        self.url = url

        self.verify = verify
        self.watcher = watcher if watcher else dummy
        self.force = force

        url_no_args = url.split("?")[0]

        base, ext = os.path.splitext(url_no_args)
        _, tar = os.path.splitext(base)
        if tar == ".tar":
            ext = ".tar" + ext

        if unpack is None:
            unpack = ext in (".tar", ".tar.gz")

        def download(target, url):
            o = urlparse(self.url)
            return DOWNLOADERS[o.scheme](self).download(url, target)

        def download_and_unpack(target, url):
            archive = target + ext
            download(archive, url)
            LOG.info("Unpacking...")
            shutil.unpack_archive(archive, target)
            LOG.info("Done.")
            os.unlink(archive)

        if unpack:
            self.path = self.cache_file(
                download_and_unpack,
                url,
                extension=".d",
                force=self.force,
            )
        else:
            self.path = self.cache_file(
                download,
                url,
                extension=ext,
                force=self.force,
            )

    def __repr__(self) -> str:
        return f"Url({self.url})"


source = Url
