# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
from .base import FileSource
import requests
from tqdm import tqdm
import shutil
import xarray as xr


class ZipUrl(FileSource):
    def __init__(self, url):
        self.path = self.cache_file(url)

        base, ext = os.path.splitext(url)
        _, tar = os.path.splitext(base)
        if tar == ".tar":
            ext = ".tar" + ext

        directory = self.path
        download = self.path + ".download" + ext
        if not os.path.exists(directory):
            if not os.path.exists(download):
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
                    with open(download + ".tmp", mode) as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                total += len(chunk)
                                pbar.update(len(chunk))
                os.rename(download + ".tmp", download)
            print()
            print("Unpacking...")
            if not os.path.exists(directory + ".tmp"):
                os.mkdir(directory + ".tmp")

            # See https://docs.python.org/3/library/shutil.html#shutil.get_archive_formats
            shutil.unpack_archive(download, directory + ".tmp")

            print("Done...")
            os.rename(directory + ".tmp", directory)
            os.unlink(download)

        paths = []
        for root, _, files in os.walk(directory):
            for f in files:
                paths.append(os.path.join(root, f))

        if len(paths) == 1:
            self.path = paths[0]
        else:
            self._xarray = xr.open_mfdataset(paths, combine="by_coords")  # nested

    def to_xarray(self):
        return self._xarray


source = ZipUrl
