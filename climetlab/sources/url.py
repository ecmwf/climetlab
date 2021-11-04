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
import re
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


def mimetype_to_extension(mimetype, compression, default=".unknown"):
    EXTENSIONS = {
        None: "",
        "gzip": ".gz",
        "xz": ".xz",
        "bzip2": ".bz2",
    }
    if mimetype is None:
        extension = default
    else:
        extension = mimetypes.guess_extension(mimetype)

    return extension + EXTENSIONS[compression]


def canonical_extension(path):
    _, ext = os.path.splitext(path)
    ext = mimetype_to_extension(*mimetypes.guess_type(path), default=ext)
    # Looks like mimetypes as .cdf before .nc
    # TODO: report it to Python's bug tracker
    EXTENSIONS = {".cdf": ".nc"}

    return EXTENSIONS.get(ext, ext)


class Downloader:
    def __init__(self, owner):
        # TODO: use weakref instead
        self.owner = owner

        if self.owner.parts:
            assert self.supports_parts

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
                total = self.transfer(f, pbar, self.owner.observer)

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


class DecodeMultipart:
    def __init__(self, request, parts):
        self.request = request
        assert request.status_code == 206, request.status_code

        kind, self.boundary = request.headers["content-type"].split("=")
        assert kind == "multipart/byteranges; boundary", kind

        self.size = int(request.headers["content-length"])
        self.encoding = "utf-8"
        self.parts = parts

    def __call__(self, chunk_size):
        return self.stream(chunk_size)

    def stream(self, chunk_size):
        from email.parser import HeaderParser

        from requests.structures import CaseInsensitiveDict

        header_parser = HeaderParser()
        marker = f"--{self.boundary}\r\n".encode(self.encoding)
        end_header = b"\r\n\r\n"
        end_data = b"\r\n"

        end_of_input = f"--{self.boundary}--\r\n".encode(self.encoding)

        if chunk_size < len(end_data):
            chunk_size = len(end_data)

        iter_content = self.request.iter_content(chunk_size)
        chunk = next(iter_content)

        # Some servers start with \r\n
        if chunk[:2] == end_data:
            chunk = chunk[2:]

        LOG.debug("MARKER %s", marker)
        part = 0
        while True:
            while len(chunk) < max(len(marker), len(end_of_input)):
                more = next(iter_content)
                assert more is not None
                chunk += more

            if chunk.find(end_of_input) == 0:
                assert part == len(self.parts)
                break

            pos = chunk.find(marker)
            assert pos == 0, (pos, chunk)

            chunk = chunk[pos + len(marker) :]
            while True:
                pos = chunk.find(end_header)
                if pos != -1:
                    break
                more = next(iter_content)
                assert more is not None
                chunk += more
                assert len(chunk) < 1024 * 16

            pos += len(end_header)
            header = chunk[:pos].decode(self.encoding)
            header = CaseInsensitiveDict(header_parser.parsestr(header))
            chunk = chunk[pos:]
            # kind = header["content-type"]
            bytes = header["content-range"]
            LOG.debug("HEADERS %s", header)
            m = re.match(r"^bytes (\d+)d?-(\d+)d?/(\d+)d?$", bytes)
            assert m, header
            start, end, total = int(m.group(1)), int(m.group(2)), int(m.group(3))

            assert end >= start
            assert start < total
            assert end < total

            size = end - start + 1

            assert start == self.parts[part][0]
            assert end == self.parts[part][0] + self.parts[part][1] - 1

            while size > 0:
                if len(chunk) >= size:
                    yield chunk[:size]
                    chunk = chunk[size:]
                    size = 0
                else:
                    yield chunk
                    size -= len(chunk)
                    chunk = next(iter_content)

            assert chunk.find(end_data) == 0
            chunk = chunk[len(end_data) :]
            part += 1


class HTTPDownloader(Downloader):
    supports_parts = True

    _headers = None
    _url = None

    def headers(self, url):
        if self._headers is None or url != self._url:
            self._url = url
            self._headers = {}
            if self.owner.fake_headers is not None:
                self._headers = dict(**self.owner.fake_headers)
            else:
                try:
                    r = requests.head(
                        url,
                        headers=self.owner.http_headers,
                        verify=self.owner.verify,
                        allow_redirects=True,
                    )
                    r.raise_for_status()
                    for k, v in r.headers.items():
                        self._headers[k.lower()] = v
                    LOG.debug(
                        "HTTP headers %s",
                        json.dumps(self._headers, sort_keys=True, indent=4),
                    )
                except Exception:
                    self._url = None
                    self._headers = {}
                    LOG.exception("HEAD %s", url)
        return self._headers

    def extension(self, url):

        ext = super().extension(url)

        if ext == ".unknown":
            # Only check for "content-disposition" if
            # the URL does not end with an extension
            # so we avoid fetching the headers unesseraly

            headers = self.headers(url)

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

    def prepare(self, url, download):

        size = None
        mode = "wb"
        skip = 0

        parts = self.owner.parts

        headers = self.headers(url)
        if "content-length" in headers:
            try:
                size = int(headers["content-length"])
            except Exception:
                LOG.exception("content-length %s", url)

        # content-length is the size of the encoded body
        # so we cannot rely on it to check the file size
        encoded = headers.get("content-encoding") is not None

        http_headers = dict(**self.owner.http_headers)

        if not parts and not encoded and os.path.exists(download):

            bytes = os.path.getsize(download)

            if size is not None:
                assert bytes < size, (bytes, size, url, download)

            if bytes > 0:
                if headers.get("accept-ranges") == "bytes":
                    mode = "ab"
                    http_headers["range"] = f"bytes={bytes}-"
                    LOG.info(
                        "%s: resuming download from byte %s",
                        download,
                        bytes,
                    )
                    skip = bytes
                else:
                    LOG.warning(
                        "%s: %s bytes already download, but server does not support restarts",
                        download,
                        bytes,
                    )

        if parts:
            if headers.get("accept-ranges") != "bytes":
                raise ValueError(f"Server for {url} does not support byte ranges")
            # We can trust the size
            encoded = None
            size = sum(p[1] for p in parts)
            ranges = []
            for offset, length in parts:
                ranges.append(f"{offset}-{offset+length-1}")
            http_headers["range"] = f"bytes={','.join(ranges)}"

        r = requests.get(
            url,
            stream=True,
            verify=self.owner.verify,
            timeout=SETTINGS.get("url-download-timeout"),
            headers=http_headers,
        )
        r.raise_for_status()

        self.stream = r.iter_content
        if parts and len(parts) > 1:
            self.stream = DecodeMultipart(r, parts)

        LOG.debug(
            "url prepare size=%s mode=%s skip=%s encoded=%s",
            size,
            mode,
            skip,
            encoded,
        )
        return size, mode, skip, encoded

    def transfer(self, f, pbar, watcher):
        total = 0
        for chunk in self.stream(chunk_size=1024 * 1024):
            watcher()
            if chunk:
                f.write(chunk)
                total += len(chunk)
                pbar.update(len(chunk))
        return total

    def cache_data(self, url):
        return self.headers(url)

    def out_of_date(self, url, path, cache_data):

        if SETTINGS.get("check-out-of-date-urls"):
            return False

        if cache_data is not None:

            # TODO: check 'cache-control' to see if we should check the etag
            if "cache-control" in cache_data:
                pass

            if "expires" in cache_data:
                if cache_data["expires"] != "0":  # HTTP1.0 legacy
                    try:
                        expires = parse_date(cache_data["expires"])
                        now = pytz.UTC.localize(datetime.datetime.utcnow())
                        if expires > now:
                            LOG.debug("URL %s not expired (%s > %s)", url, expires, now)
                            return False
                    except Exception:
                        LOG.exception(
                            "Failed to check URL expiry date '%s'",
                            cache_data["expires"],
                        )

            try:
                headers = self.headers(url)
            except requests.exceptions.ConnectionError:
                return False

            cached_etag = cache_data.get("etag")
            remote_etag = headers.get("etag")

            if cached_etag != remote_etag and remote_etag is not None:
                LOG.warning("Remote content of URL %s has changed", url)
                if (
                    SETTINGS.get("download-out-of-date-urls")
                    or self.owner.update_if_out_of_date
                ):
                    LOG.warning("Invalidating cache version and re-downloading %s", url)
                    return True
                LOG.warning(
                    "To enable automatic downloading of updated URLs set the 'download-out-of-date-urls'"
                    " setting to True",
                )
            else:
                LOG.debug("Remote content of URL %s unchanged", url)

        return False


class FTPDownloader(Downloader):

    supports_parts = False

    def prepare(self, url, download):

        mode = "wb"

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

        return ftp.size(self.filename), mode, 0, False

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
                    chunk = g.read(min(length, 1024 * 1024))
                    assert chunk
                    f.write(chunk)
                    length -= len(chunk)
                    total += len(chunk)
                    pbar.update(len(chunk))
        return total


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
        parts=None,
        offsets=None,
        lengths=None,
        filter=None,
        merger=None,
        verify=True,
        force=None,
        # extension=None,
        http_headers=None,
        update_if_out_of_date=False,
        mirror=DEFAULT_MIRROR,
        fake_headers=None,  # When HEAD is not allowed but you know the size
    ):
        # TODO: re-enable this feature
        extension = None

        self.url = url
        LOG.debug("URL %s", url)

        self.filter = filter
        self.merger = merger
        self.verify = verify
        self.update_if_out_of_date = update_if_out_of_date
        self.http_headers = http_headers if http_headers else {}
        self.fake_headers = fake_headers

        if parts is not None:
            assert offsets is None and lengths is None
            offsets = [p[0] for p in parts]
            lengths = [p[1] for p in parts]

        self.parts = None
        if offsets is not None or lengths is not None:
            assert len(offsets) == len(lengths)
            self.parts = []
            last = -1
            # Compress and check
            for offset, length in zip(offsets, lengths):
                assert offset >= 0 and length > 0
                assert offset >= last, (
                    f"Offsets and lengths must be in order, and not overlapping:"
                    f" offset={offset}, end of previous part={last}"
                )
                if offset == last:
                    # Compress
                    offset, prev_length = self.parts.pop()
                    length += prev_length

                self.parts.append((offset, length))
                last = offset + length

            if len(self.parts) == 0:
                self.parts = None

        if mirror:
            assert self.parts is None
            url = mirror(url)

        o = urlparse(url)
        downloader = DOWNLOADERS[o.scheme](self)

        if extension and extension[0] != ".":
            extension = "." + extension

        if extension is None:
            extension = downloader.extension(url)

        self.path = downloader.local_path(url)
        if self.path is not None:
            return

        if force is None:
            force = downloader.out_of_date

        def download(target, url):
            downloader.download(url, target)
            return downloader.cache_data(url)

        self.path = self.cache_file(
            download,
            url,
            extension=extension,
            force=force,
            hash_extra=self.parts,
        )

    def __repr__(self) -> str:
        return f"Url({self.url})"


source = Url
