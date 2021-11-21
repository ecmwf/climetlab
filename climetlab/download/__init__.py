# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import mimetypes
import os
from urllib.parse import urlparse

from .file import FullFileDownloader, PartFileDownloader
from .ftp import FullFTPDownloader, PartFTPDownloader
from .heuristics import Part
from .http import FullHTTPDownloader, PartHTTPDownloader
from .multipart import compress_parts

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


DOWNLOADERS = {
    ("ftp", False): FullFTPDownloader,
    ("ftp", True): PartFTPDownloader,
    ("http", False): FullHTTPDownloader,
    ("http", True): PartHTTPDownloader,
    ("https", False): FullHTTPDownloader,
    ("https", True): PartHTTPDownloader,
    ("file", False): FullFileDownloader,
    ("file", True): PartFileDownloader,
}


def get_downloader(url, **kwargs):

    parts = kwargs.get("parts")
    if parts is not None:
        parts = [Part(offset, length) for offset, length in parts]
        parts = compress_parts(parts)
        if len(parts) == 0:
            parts = None
        kwargs["parts"] = parts

    o = urlparse(url)
    has_parts = parts is not None and len(parts) > 0

    downloader = DOWNLOADERS[(o.scheme, has_parts)](url, **kwargs)

    return downloader
