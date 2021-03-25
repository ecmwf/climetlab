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
from tqdm import tqdm

from .base import FileSource

LOG = logging.getLogger(__name__)


class Url(FileSource):
    def __init__(self, url, unpack=None, **kwargs):

        super().__init__(**kwargs)

        base, ext = os.path.splitext(url)
        _, tar = os.path.splitext(base)
        if tar == ".tar":
            ext = ".tar" + ext

        if unpack is None:
            unpack = ext in (".tar", ".tar.gz")

        if unpack:
            self.path = self.cache_file(url, extension=".d")
            if not os.path.exists(self.path):
                archive = self.path + ext
                self.download(url, archive)
                self.unpack(archive, self.path)
                os.unlink(archive)
        else:
            _, ext = os.path.splitext(url)
            self.path = self.cache_file(url, extension=ext)
            if not os.path.exists(self.path):
                self.download(url, self.path)

    def download(self, url, target):

        if os.path.exists(target):
            return

        LOG.info("Downloading %s", url)
        download = target + ".download"
        r = requests.head(url)
        r.raise_for_status()
        try:
            size = int(r.headers["content-length"])
        except Exception:
            size = None
        r = requests.get(url, stream=True)
        r.raise_for_status()
        total = 0
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
            pbar.update(total)
            with open(download, mode) as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        total += len(chunk)
                        pbar.update(len(chunk))

        os.rename(download, target)

    def unpack(self, archive, directory):
        if os.path.exists(directory):
            return
        LOG.info("Unpacking...")
        target = directory + ".tmp"
        if not os.path.exists(target):
            os.mkdir(target)

        shutil.unpack_archive(archive, target)
        os.rename(target, directory)
        LOG.info("Done.")


source = Url
