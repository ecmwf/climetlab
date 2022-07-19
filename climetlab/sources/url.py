# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging

from multiurl import Downloader

from climetlab.core.caching import cache_file
from climetlab.core.settings import SETTINGS
from climetlab.core.statistics import record_statistics
from climetlab.utils import progress_bar

from .file import FileSource

LOG = logging.getLogger(__name__)


def download_and_cache(
    url,
    *,
    owner="url",
    parts=None,
    verify=True,
    force=None,
    chunk_size=1024 * 1024,
    range_method="auto",
    http_headers=None,
    update_if_out_of_date=False,
    fake_headers=None,  # When HEAD is not allowed but you know the size
    **kwargs,
):

    # TODO: re-enable this feature
    extension = None

    LOG.debug("URL %s", url)

    downloader = Downloader(
        url,
        chunk_size=chunk_size,
        timeout=SETTINGS.get("url-download-timeout"),
        verify=verify,
        parts=parts,
        range_method=range_method,
        http_headers=http_headers,
        fake_headers=fake_headers,
        statistics_gatherer=record_statistics,
        progress_bar=progress_bar,
        resume_transfers=True,
        override_target_file=False,
        download_file_extension=".download",
    )

    if extension and extension[0] != ".":
        extension = "." + extension

    if extension is None:
        extension = downloader.extension()

    path = downloader.local_path()
    if path is not None:
        return

    def out_of_date(url, path, cache_data):
        if SETTINGS.get("check-out-of-date-urls") is False:
            return False

        if downloader.out_of_date(path, cache_data):
            if SETTINGS.get("download-out-of-date-urls") or update_if_out_of_date:
                LOG.warning(
                    "Invalidating cache version and re-downloading %s",
                    url,
                )
                return True
            else:
                LOG.warning(
                    "To enable automatic downloading of updated URLs set the 'download-out-of-date-urls'"
                    " setting to True",
                )
        return False

    if force is None:
        force = out_of_date

    def download(target, _):
        downloader.download(target)
        return downloader.cache_data()

    path = cache_file(
        owner,
        download,
        dict(url=url, parts=parts),
        extension=extension,
        force=force,
    )

    return path


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
        range_method="auto",
        http_headers=None,
        update_if_out_of_date=False,
        fake_headers=None,  # When HEAD is not allowed but you know the size
    ):

        super().__init__(filter=filter, merger=merger)

        # TODO: re-enable this feature
        extension = None

        self.url = url
        self.parts = parts
        LOG.debug("URL %s", url)

        self.update_if_out_of_date = update_if_out_of_date

        self.downloader = Downloader(
            url,
            chunk_size=chunk_size,
            timeout=SETTINGS.get("url-download-timeout"),
            verify=verify,
            parts=parts,
            range_method=range_method,
            http_headers=http_headers,
            fake_headers=fake_headers,
            statistics_gatherer=record_statistics,
            progress_bar=progress_bar,
            resume_transfers=True,
            override_target_file=False,
            download_file_extension=".download",
        )

        if extension and extension[0] != ".":
            extension = "." + extension

        if extension is None:
            extension = self.downloader.extension()

        self.path = self.downloader.local_path()
        if self.path is not None:
            return

        if force is None:
            force = self.out_of_date

        def download(target, _):
            self.downloader.download(target)
            return self.downloader.cache_data()

        self.path = self.cache_file(
            download,
            dict(url=url, parts=parts),
            extension=extension,
            force=force,
        )

    def connect_to_mirror(self, mirror):
        return mirror.connection_for_url(self, self.url, self.parts)

    def out_of_date(self, url, path, cache_data):
        if SETTINGS.get("check-out-of-date-urls") is False:
            return False

        if self.downloader.out_of_date(path, cache_data):
            if SETTINGS.get("download-out-of-date-urls") or self.update_if_out_of_date:
                LOG.warning(
                    "Invalidating cache version and re-downloading %s",
                    self.url,
                )
                return True
            else:
                LOG.warning(
                    "To enable automatic downloading of updated URLs set the 'download-out-of-date-urls'"
                    " setting to True",
                )
        return False

    def __repr__(self) -> str:
        return f"Url({self.url})"


source = Url
