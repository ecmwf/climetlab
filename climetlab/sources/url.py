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

import requests

try:
    import ipywidgets  # noqa
    from tqdm.auto import tqdm
except ImportError:
    from tqdm import tqdm

from .base import FileSource

LOG = logging.getLogger(__name__)


class Url(FileSource):
    def __init__(self, url, unpack=None, verify=True, **kwargs):

        super().__init__(**kwargs)

        self.verify = verify

        base, ext = os.path.splitext(url)
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

    def _download(self, url, target):

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
        r = requests.get(url, stream=True, verify=self.verify)
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
                    if chunk:
                        f.write(chunk)
                        total += len(chunk)
                        pbar.update(len(chunk))
            pbar.close()

        os.rename(download, target)


source = Url
