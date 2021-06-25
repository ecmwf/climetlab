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
from urllib.parse import urlparse

import requests

from climetlab.core.settings import SETTINGS
from climetlab.sources.empty import EmptySource

try:
    import ipywidgets  # noqa
    from tqdm.auto import tqdm
except ImportError:
    from tqdm import tqdm

from .base import FileSource

LOG = logging.getLogger(__name__)


def dummy():
    pass


class Url(FileSource):
    def __init__(
        self,
        url,
        unpack=None,
        file_filter=None,
        verify=True,
        watcher=None,
        **kwargs,
    ):
        self.url = url

        super().__init__(file_filter=file_filter, **kwargs)

        self.verify = verify
        self.watcher = watcher if watcher else dummy

        url_no_args = url.split("?")[0]
        if file_filter is not None and not file_filter(url_no_args):
            self.empty = True
            return

        base, ext = os.path.splitext(url_no_args)
        _, tar = os.path.splitext(base)
        if tar == ".tar":
            ext = ".tar" + ext

        if unpack is None:
            unpack = ext in (".tar", ".tar.gz")

        def download(target, url):
            return self._download(url, target)

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
            )
        else:
            self.path = self.cache_file(
                download,
                url,
                extension=ext,
            )

    def mutate(self):
        if self.path is None:
            # The download was not performed.
            # Filtered out by file_filter.
            return EmptySource()
        return self

    def _download(self, url, target):
        o = urlparse(url)
        method = f"_download_{o.scheme}"
        return getattr(self, method)(url, target)

    def _download_file(self, url, target):
        o = urlparse(url)
        assert o.scheme == "file"
        assert os.path.exists(o.path), f"File not found: {o.path}"
        os.symlink(o.path, target)

    def _download_ftp(self, url, target):
        from ftplib import FTP

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
        filename = os.path.basename(o.path)
        size = ftp.size(filename)

        with tqdm(
            total=size,
            unit_scale=True,
            unit_divisor=1024,
            unit="B",
            disable=False,
            leave=False,
            desc=os.path.basename(url),
        ) as pbar:
            with open(target, "wb") as f:

                def callback(chunk):
                    self.watcher()
                    f.write(chunk)
                    pbar.update(len(chunk))

                ftp.retrbinary(f"RETR {filename}", callback)
            pbar.close()
        ftp.close()

    def _download_https(self, url, target):
        return self._download_http(url, target)

    def _download_http(self, url, target):

        if os.path.exists(target):
            return

        download = target + ".download"
        LOG.info("Downloading %s", url)

        r = requests.head(url, verify=self.verify)
        r.raise_for_status()
        try:
            size = int(r.headers["content-length"])
        except Exception:
            size = None
        r = requests.get(
            url,
            stream=True,
            verify=self.verify,
            timeout=SETTINGS.as_seconds("url-download-timeout"),
        )
        r.raise_for_status()
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
            total = 0
            pbar.update(total)
            with open(download, mode) as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    self.watcher()
                    if chunk:
                        f.write(chunk)
                        total += len(chunk)
                        pbar.update(len(chunk))
            pbar.close()

        # take care of race condition when two processes
        # download into the same file at the same time
        try:
            os.rename(download, target)
        except FileNotFoundError as e:
            if not os.path.exists(target):
                raise e

    def __repr__(self) -> str:
        return f"Url({self.url})"


source = Url
