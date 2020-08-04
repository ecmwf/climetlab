# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import os
from . import DataSource
from climetlab.core.caching import temp_file
import requests
from tqdm import tqdm
import zipfile
import xarray as xr


class ZipUrl(DataSource):
    def __init__(self, url):
        self.path = temp_file("ZipUrl", url)

        if not os.path.exists(self.path + ".d"):
            if not os.path.exists(self.path + ".zip"):
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
                os.rename(self.path, self.path + ".zip")
            print("Unzipping...")
            if not os.path.exists(self.path + ".tmp"):
                os.mkdir(self.path + ".tmp")

            with zipfile.ZipFile(self.path + ".zip", "r") as zip_file:
                for file in tqdm(
                    iterable=zip_file.namelist(),
                    leave=False,
                    total=len(zip_file.namelist()),
                ):
                    zip_file.extract(member=file, path=self.path + ".tmp")

            print("Done...")
            os.rename(self.path + ".tmp", self.path + ".d")
            os.unlink(self.path + ".zip")

        self._xarray = xr.open_mfdataset(
            self.path + ".d/*.nc", combine="by_coords"
        )  # nested

    def to_xarray(self):
        return self._xarray


source = ZipUrl
