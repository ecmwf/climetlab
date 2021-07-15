# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import cgi
import datetime
import json
import logging
import mimetypes
import os
import sys
from ftplib import FTP
from urllib.parse import urlparse

import pytz
import requests
from dateutil.parser import parse as parse_date

from climetlab.core.settings import SETTINGS
from climetlab.utils import tqdm
from climetlab.utils.mirror import DEFAULT_MIRROR

from .file import FileSource

LOG = logging.getLogger(__name__)

OFFLINE = False  # For use with pytest


def offline(off):
    global OFFLINE
    OFFLINE = off


def dummy():
    pass


class Downloader:
    def __init__(self, owner):
        self.owner = owner

    def local_path(self, url):
        return None

    def extension(self, url):
        url_no_args = url.split("?")[0]

        base, ext = os.path.splitext(url_no_args)
        if ext == "":
            base, ext = os.path.splitext(url)

        _, tar = os.path.splitext(base)
        if tar == ".tar":
            ext = ".tar" + ext

        return ext

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
            desc=self.title(url),
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

    def title(self, url):
        return os.path.basename(url)

    def cache_data(sel, url):
        return None

    def out_of_date(self, url, path, cache_data):
        return False


class HTTPDownloader(Downloader):

    _headers = None
    _url = None

    def headers(self, url):
        if self._headers is None or url != self._url:
            self._url = url
            self._headers = {}
            try:
                r = requests.head(url, verify=self.owner.verify, allow_redirects=True)
                r.raise_for_status()
                for k, v in r.headers.items():
                    self._headers[k.lower()] = v
                LOG.debug(
                    "HTTP headers %s",
                    json.dumps(self._headers, sort_keys=True, indent=4),
                )
            except Exception:
                LOG.exception("HEAD %s", url)
        return self._headers

    def extension(self, url):
        EXCEPTIONS = (".tgz", ".tar.gz")

        headers = self.headers(url)

        ext = super().extension(url)

        if ext not in EXCEPTIONS:
            if "content-type" in headers:
                if headers["content-type"] != "application/octet-stream":
                    ext = mimetypes.guess_extension(headers["content-type"])

        if "content-disposition" in headers:
            value, params = cgi.parse_header(headers["content-disposition"])
            assert value == "attachment", value
            if "filename" in params:
                ext = super().extension(params["filename"])

        return ext

    def title(self, url):
        headers = self.headers(url)
        if "content-disposition" in headers:
            value, params = cgi.parse_header(headers["content-disposition"])
            assert value == "attachment", value
            if "filename" in params:
                return params["filename"]
        return super().title(url)

    def prepare(self, url):

        size = None
        headers = self.headers(url)
        if "content-length" in headers:
            try:
                size = int(headers["content-length"])
            except Exception:
                LOG.exception("content-length %s", url)

        r = requests.get(
            url,
            stream=True,
            verify=self.owner.verify,
            timeout=SETTINGS.get("url-download-timeout"),
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

    def cache_data(self, url):
        return self.headers(url)

    def out_of_date(self, url, path, cache_data):
        if cache_data is not None:

            # TODO: check 'cache-control' to see if we should check the etag
            if "cache-control" in cache_data:
                pass

            if "expires" in cache_data:
                try:
                    expires = parse_date(cache_data["expires"])
                    now = pytz.UTC.localize(datetime.datetime.utcnow())
                    if expires > now:
                        LOG.debug("URL %s not expired (%s > %s)", url, expires, now)
                        return False
                except Exception:
                    LOG.exception(
                        "Failed to check URL expiry date '%s'", cache_data["expires"]
                    )

            headers = self.headers(url)
            cached_etag = cache_data.get("etag")
            remote_etag = headers.get("etag")

            if cached_etag != remote_etag:
                LOG.warning("Remote content of URL %s has changed", url)
                if SETTINGS.get("download-updated-urls"):
                    LOG.warning("Invalidating cache version and re-downloading %s", url)
                    return True
                LOG.warning(
                    "To enable automatic downloading of updated URLs set the 'download-updated-urls' setting to True",
                )
            else:
                LOG.debug("Remote content of URL %s unchanged", url)

        return False


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
            timeout=SETTINGS.get("url-download-timeout"),
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

        return path


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
        filter=None,
        merger=None,
        verify=True,
        watcher=None,
        force=None,
        mirror=DEFAULT_MIRROR,
        **kwargs,
    ):
        self.url = url
        LOG.debug("URL %s", url)

        self.filter = filter
        self.merger = merger
        self.verify = verify
        self.watcher = watcher if watcher else dummy

        if mirror:
            url = mirror(url)

        o = urlparse(url)
        downloader = DOWNLOADERS[o.scheme](self)
        extension = downloader.extension(url)

        self.path = downloader.local_path(url)
        if self.path is not None:
            return

        if force is None:
            force = downloader.out_of_date

        def download(target, url):
            assert not OFFLINE
            downloader.download(url, target)
            return downloader.cache_data(url)

        self.path = self.cache_file(
            download,
            url,
            extension=extension,
            force=force,
        )

    def __repr__(self) -> str:
        return f"Url({self.url})"


source = Url
