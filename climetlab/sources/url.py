# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging

from climetlab.core.settings import SETTINGS
from climetlab.download import get_downloader
from climetlab.download.multipart import compress_parts
from climetlab.utils.mirror import DEFAULT_MIRROR

from .file import FileSource

LOG = logging.getLogger(__name__)


class Url(FileSource):
    def __init__(
        self,
        url,
        parts=None,
        filter=None,
        merger=None,
        verify=True,
        force=None,
        chunk_size=1024 * 1024,
        # extension=None,
        range_method="auto",
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
            parts = compress_parts(parts)
            if len(parts) == 0:
                parts = None

        if mirror:
            url = mirror(url)

        downloader = get_downloader(
            url,
            chunk_size=chunk_size,
            timeout=SETTINGS.get("url-download-timeout"),
            verify=verify,
            parts=parts,
            http_headers=http_headers,
            fake_headers=fake_headers,
        )

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
            hash_extra=parts,
        )

    def __repr__(self) -> str:
        return f"Url({self.url})"


source = Url
