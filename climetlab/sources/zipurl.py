# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import os
from .base import FileSource
from climetlab.core.caching import cache_file
import requests
from tqdm import tqdm
import shutil
import xarray as xr


class ZipUrl(FileSource):
    def __init__(self, url):
        self.path = cache_file("ZipUrl", url)

        base, ext = os.path.splitext(url)
        _, tar = os.path.splitext(base)
        if tar == '.tar':
            ext = '.tar' + ext

        if not os.path.exists(self.path + ".d"):
            if not os.path.exists(self.path + ext):
                print("Downloading", url)
                r = requests.head(url)
                r.raise_for_status()
                size = int(r.headers["content-length"])

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
                ) as pbar:
                    pbar.update(total)
                    with open(self.path, mode) as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                total += len(chunk)
                                pbar.update(len(chunk))
                os.rename(self.path, self.path + ext)
            print("Unpacking...")
            if not os.path.exists(self.path + ".tmp"):
                os.mkdir(self.path + ".tmp")

            shutil.unpack_archive(self.path + ext, self.path + ".tmp")

            print("Done...")
            os.rename(self.path + ".tmp", self.path + ".d")
            os.unlink(self.path + ext)

        paths = []
        for root, _, files in os.walk(self.path + ".d"):
            for f in files:
                paths.append(os.path.join(root, f))

        if len(paths) == 1:
            self.path = paths[0]
        else:
            self._xarray = xr.open_mfdataset(paths, combine="by_coords")  # nested

    def to_xarray(self):
        return self._xarray


source = ZipUrl
