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
import os
import time

import pytz
import requests
from dateutil.parser import parse as parse_date

from climetlab.core.settings import SETTINGS
from climetlab.core.statistics import record_statistics

from .downloader import Downloader
from .multipart import DecodeMultipart, PartFilter, compute_byte_ranges

LOG = logging.getLogger(__name__)


def NoFilter(x):
    return x


class HTTPDownloader(Downloader):
    supports_parts = True

    def __init__(
        self,
        url,
        verify=True,
        http_headers=None,
        fake_headers=None,
        range_method=None,
        **kwargs,
    ):
        super().__init__(url, **kwargs)
        self._headers = None
        self._url = None
        self.http_headers = http_headers if http_headers else {}
        self.verify = verify
        self.fake_headers = fake_headers
        self.range_method = range_method

    def headers(self, url):
        if self._headers is None or url != self._url:
            self._url = url
            self._headers = {}
            if self.fake_headers is not None:
                self._headers = dict(**self.fake_headers)
            else:
                try:
                    r = requests.head(
                        url,
                        headers=self.http_headers,
                        verify=self.verify,
                        timeout=self.timeout,
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

        parts = self.parts

        headers = self.headers(url)
        if "content-length" in headers:
            try:
                size = int(headers["content-length"])
            except Exception:
                LOG.exception("content-length %s", url)

        # content-length is the size of the encoded body
        # so we cannot rely on it to check the file size
        encoded = headers.get("content-encoding") is not None

        http_headers = dict(**self.http_headers)

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

        range_method = self.range_method

        filter = NoFilter

        if parts:
            # We can trust the size
            encoded = None
            size = sum(p[1] for p in parts)
            if headers.get("accept-ranges") != "bytes":
                LOG.warning(
                    "Server for %s does not support byte ranges, downloading whole file",
                    url,
                )
                filter = PartFilter(parts)
                parts = None
            else:
                ranges = []
                if range_method:

                    rounded, positions = compute_byte_ranges(parts, range_method, url)
                    filter = PartFilter(parts, positions)
                    parts = rounded

                for offset, length in parts:
                    ranges.append(f"{offset}-{offset+length-1}")

                http_headers["range"] = f"bytes={','.join(ranges)}"

                # print("RANGES", http_headers["range"])

        r = requests.get(
            url,
            stream=True,
            verify=self.verify,
            timeout=self.timeout,
            headers=http_headers,
        )
        try:
            r.raise_for_status()
        except Exception:
            LOG.error("URL %s: %s", url, r.text)
            raise

        if parts and len(parts) > 1:
            self.stream = filter(
                DecodeMultipart(
                    url,
                    r,
                    parts,
                    verify=self.verify,
                    timeout=self.timeout,
                    headers=http_headers,
                )
            )
        else:
            self.stream = filter(r.iter_content)

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
        start = time.time()
        for chunk in self.stream(chunk_size=self.chunk_size):
            watcher()
            if chunk:
                f.write(chunk)
                total += len(chunk)
                pbar.update(len(chunk))

        record_statistics(
            "transfer",
            url=self.url,
            total=total,
            elapsed=time.time() - start,
        )
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
                    or self.update_if_out_of_date
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
