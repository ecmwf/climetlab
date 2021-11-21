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

from .downloader import Downloader
from .multipart import DecodeMultipart, PartFilter, compute_byte_ranges

LOG = logging.getLogger(__name__)


def NoFilter(x):
    return x


class HTTPDownloaderBase(Downloader):
    supports_parts = True

    def __init__(
        self,
        url,
        verify=True,
        http_headers=None,
        fake_headers=None,
        range_method=None,
        retry_max=500,
        sleep_max=120,
        **kwargs,
    ):
        super().__init__(url, **kwargs)
        self._headers = None
        self._url = None
        self.http_headers = http_headers if http_headers else {}
        self.verify = verify
        self.fake_headers = fake_headers
        self.range_method = range_method
        self.sleep_max = sleep_max
        self.retry_max = retry_max

    def headers(self):
        if self._headers is None or self.url != self._url:
            self._url = self.url
            self._headers = {}
            if self.fake_headers is not None:
                self._headers = dict(**self.fake_headers)
            else:
                try:
                    r = self.robust(requests.head)(
                        self.url,
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
                    LOG.exception("HEAD %s", self.url)
        return self._headers

    def extension(self):

        ext = super().extension()

        if ext == ".unknown":
            # Only check for "content-disposition" if
            # the URL does not end with an extension
            # so we avoid fetching the headers unesseraly

            headers = self.headers()

            if "content-disposition" in headers:
                value, params = cgi.parse_header(headers["content-disposition"])
                assert value == "attachment", value
                if "filename" in params:
                    ext = super().extension(params["filename"])

        return ext

    def title(self):
        headers = self.headers()
        if "content-disposition" in headers:
            value, params = cgi.parse_header(headers["content-disposition"])
            assert value == "attachment", value
            if "filename" in params:
                return params["filename"]
        return super().title()

    def transfer(self, f, pbar):
        total = 0
        start = time.time()
        for chunk in self.stream(chunk_size=self.chunk_size):
            self.observer()
            if chunk:
                f.write(chunk)
                total += len(chunk)
                pbar.update(len(chunk))

        self.statistics_gatherer(
            "transfer",
            url=self.url,
            total=total,
            elapsed=time.time() - start,
        )
        return total

    def cache_data(self):
        return self.headers()

    def out_of_date(self, path, cache_data):

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
                            LOG.debug(
                                "URL %s not expired (%s > %s)", self.url, expires, now
                            )
                            return False
                    except Exception:
                        LOG.exception(
                            "Failed to check URL expiry date '%s'",
                            cache_data["expires"],
                        )

            try:
                headers = self.headers()
            except requests.exceptions.ConnectionError:
                return False

            cached_etag = cache_data.get("etag")
            remote_etag = headers.get("etag")

            if cached_etag != remote_etag and remote_etag is not None:
                LOG.warning("Remote content of URL %s has changed", self.url)
                return True
            else:
                LOG.debug("Remote content of URL %s unchanged", self.url)

        return False

    def check_for_restarts(self, target):
        if not os.path.exists(target):
            return 0

        # Check if we can restarts the transfer
        # TODO: check etags... the file may have changed since

        bytes = os.path.getsize(target)

        if bytes > 0:
            headers = self.headers()
            if headers.get("accept-ranges") != "bytes":
                LOG.warning(
                    "%s: %s bytes already download, but server does not support restarts",
                    target,
                    bytes,
                )
                return 0

            LOG.info(
                "%s: resuming download from byte %s",
                target,
                bytes,
            )

        return bytes

    def issue_request(self, bytes_ranges=None):
        headers = {}
        headers.update(self.http_headers)
        if bytes_ranges is not None:
            headers["range"] = bytes_ranges

        r = self.robust(requests.get)(
            self.url,
            stream=True,
            verify=self.verify,
            timeout=self.timeout,
            headers=headers,
        )
        try:
            r.raise_for_status()
        except Exception:
            LOG.error("URL %s: %s", self.url, r.text)
            raise
        return r

    def robust(self, call):
        def retriable(code):

            return code in (
                requests.codes.internal_server_error,
                requests.codes.bad_gateway,
                requests.codes.service_unavailable,
                requests.codes.gateway_timeout,
                requests.codes.too_many_requests,
                requests.codes.request_timeout,
            )

        def wrapped(*args, **kwargs):
            tries = 0
            while tries < self.retry_max:
                try:
                    r = call(*args, **kwargs)
                except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ReadTimeout,
                ) as e:
                    r = None
                    LOG.warning(
                        "Recovering from connection error [%s], attemps %s of %s",
                        e,
                        tries,
                        self.retry_max,
                    )

                if r is not None:
                    if not retriable(r.status_code):
                        return r
                    LOG.warning(
                        "Recovering from HTTP error [%s %s], attemps %s of %s",
                        r.status_code,
                        r.reason,
                        tries,
                        self.retry_max,
                    )

                tries += 1

                LOG.warning("Retrying in %s seconds", self.sleep_max)
                time.sleep(self.sleep_max)
                LOG.info("Retrying now...")

        return wrapped


class FullHTTPDownloader(HTTPDownloaderBase):
    def prepare(self, target):
        assert self.parts is None

        size = None
        mode = "wb"
        skip = 0

        headers = self.headers()
        if "content-length" in headers:
            try:
                size = int(headers["content-length"])
            except Exception:
                LOG.exception("content-length %s", self.url)

        # content-length is the size of the encoded body
        # so we cannot rely on it to check the file size
        trust_size = size is not None and headers.get("content-encoding") is None

        # Check if we can restarts the transfer

        range = None
        bytes = self.check_for_restarts(target)
        if bytes > 0:
            assert size is None or bytes < size, (bytes, size, self.url, target)
            skip = bytes
            mode = "ab"
            range = f"bytes={bytes}-"

        r = self.issue_request(range)

        self.stream = r.iter_content

        LOG.debug(
            "url prepare size=%s mode=%s skip=%s trust_size=%s",
            size,
            mode,
            skip,
            trust_size,
        )
        return (size, mode, skip, trust_size)


class PartHTTPDownloader(HTTPDownloaderBase):
    def prepare(self, target):
        assert self.parts is not None

        headers = self.headers()
        if headers.get("accept-ranges") != "bytes":
            return self.bytes_range_not_supported(target)

        if len(self.parts) == 1:
            return self.one_part_only(target)

        return self.multi_parts(target)

    def bytes_range_not_supported(self, target):
        LOG.warning(
            "Server for %s does not support byte ranges, downloading whole file",
            self.url,
        )

        request = self.issue_request()
        self.stream = PartFilter(self.parts)(request.iter_content)

        size = sum(p.length for p in self.parts)
        return (size, "wb", 0, True)

    def one_part_only(self, target):
        # Special case, we let HTTP to its job, so we can resume transfers if needed
        assert len(self.parts) == 1

        offset, length = self.parts[0]
        start = offset
        end = offset + length - 1
        bytes = self.check_for_restarts(target)
        if bytes > 0:
            start += bytes
            skip = bytes
            mode = "ab"
        else:
            skip = 0
            mode = "wb"

        bytes_range = f"bytes={start}-{end}"
        request = self.issue_request(bytes_range)
        self.stream = request.iter_content

        size = sum(p.length for p in self.parts)
        return (size, mode, skip, True)

    def split_large_requests(self, parts):
        ranges = []
        for offset, length in parts:
            ranges.append(f"{offset}-{offset+length-1}")

        # Nginx default is 4K
        # https://stackoverflow.com/questions/686217/maximum-on-http-header-values
        bytes_range = f"bytes={','.join(ranges)}"

        if len(bytes_range) <= 4000:
            return [(bytes_range, parts)]

        middle = len(parts) // 2
        return self.split_large_requests(parts[:middle]) + self.split_large_requests(
            parts[middle:]
        )

    def multi_parts(self, target):

        # TODO: implement transfer restarts by trimming the list of parts

        filter = NoFilter
        parts = self.parts

        if self.range_method:

            rounded, positions = compute_byte_ranges(
                self.parts,
                self.range_method,
                self.url,
                self.statistics_gatherer,
            )
            filter = PartFilter(self.parts, positions)
            parts = rounded

        splits = self.split_large_requests(parts)

        def iterate_requests(chunk_size):

            for bytes_ranges, parts in splits:

                request = self.issue_request(bytes_ranges)

                stream = DecodeMultipart(
                    self.url,
                    request,
                    parts,
                    verify=self.verify,
                    timeout=self.timeout,
                    headers=self.http_headers,
                )

                yield from stream(chunk_size)

        self.stream = filter(iterate_requests)

        size = sum(p.length for p in self.parts)
        return (size, "wb", 0, True)
